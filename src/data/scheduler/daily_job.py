"""每日数据计算任务编排。[default]

定时任务流程:
1. 加载ETF计算样本
2. 为每个ETF生成/获取最近22个交易日的Mock行情数据
3. 计算四因子: 热度[mock]、动量[default]、流动性[default]、低波[default]
4. 计算排名分数与ETF综合评分
5. 计算标签 (大盘标签+个基标签)
6. 加载Mock赛道映射和资讯数据
7. 写入历史分数表
8. 刷新缓存

幂等设计:
- 同一天多次运行结果一致
- 所有写入使用INSERT OR REPLACE / ON CONFLICT UPDATE
- 因子计算基于确定性公式

降级策略 [default]:
- 某ETF数据不足时跳过该ETF，不影响其他ETF
- 某因子计算失败时该因子记为None，参与排名时排最后
- DB不可用时终止任务
"""

import json
import os
import random
from datetime import datetime, timedelta

from src.data.schema.migration import get_connection, migrate
from src.data.models.data_access import (
    load_etf_samples,
    get_active_etf_samples,
    upsert_daily_data,
    get_daily_data_window,
    upsert_factors,
    upsert_rankings,
    upsert_labels,
    load_sector_mapping,
    insert_history_scores,
    load_mock_news,
)
from src.data.calculations.heat_factor import calc_heat_factor
from src.data.calculations.momentum_factor import calc_momentum_factor, calc_20d_momentum_median
from src.data.calculations.liquidity_factor import calc_liquidity_factor
from src.data.calculations.lowvol_factor import calc_lowvol_factor
from src.data.calculations.ranking import compute_all_rankings
from src.data.calculations.labels import calc_market_tag, get_mock_fund_tags
from src.data.cache.cache_manager import cache


# ---- Mock 数据生成 ----

def generate_mock_daily_data(etf_code: str, base_date: str, days: int = 22) -> list:
    """为单个ETF生成Mock日线数据（T日至T-(days-1)日）。

    基于ETF代码的hash生成确定性随机数据，保证幂等。

    数据状态:
    - close_price: [default] 模拟收盘价(unitNav替代), 1.0~5.0
    - turnover: [default] 模拟成交额(元), 1e7~1e10
    - sousuo_uv 等: [mock] 热度原始字段
    """
    seed = hash(etf_code) % 10000
    rng = random.Random(seed)
    base_dt = datetime.strptime(base_date, "%Y-%m-%d")

    records = []
    base_close = rng.uniform(1.0, 5.0)
    base_turnover = rng.uniform(1e7, 1e10)

    for offset in range(days):
        dt = base_dt - timedelta(days=offset)
        date_str = dt.strftime("%Y-%m-%d")
        # 模拟收盘价: 在基准价附近随机波动
        close_price = round(base_close * (1 + rng.uniform(-0.03, 0.03)), 4)
        base_close = close_price
        # 模拟成交额
        turnover = round(base_turnover * (0.5 + rng.random()), 2)
        base_turnover = turnover
        # Mock热度原始字段
        sousuo_uv = round(rng.uniform(100, 10000), 0)
        sousuo_click_uv = round(sousuo_uv * rng.uniform(0.1, 0.5), 0)
        fenshi_uv = round(rng.uniform(200, 20000), 0)
        add_uv = round(rng.uniform(10, 500), 0)
        buy_uv = round(rng.uniform(1, 100), 0)

        records.append((
            etf_code, date_str, close_price, turnover,
            sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv,
        ))

    return records


# ---- 主任务 ----

def run_daily_job(target_date: str = None, config_dir: str = None):
    """执行每日早盘宝数据计算任务。

    Args:
        target_date: 目标计算日期 (默认今天)
        config_dir: 配置文件目录

    Returns:
        {status, date, etf_count, top5, errors}
    """
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    if config_dir is None:
        config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "config",
        )

    # 1. 初始化DB
    migrate()
    conn = get_connection()
    errors = []

    try:
        # 2. 加载ETF样本和配置
        samples_path = os.path.join(config_dir, "etf_samples.json")
        sector_path = os.path.join(config_dir, "sector_mapping.json")
        tags_path = os.path.join(config_dir, "fund_tags.json")
        news_path = os.path.join(config_dir, "mock_news.json")

        with open(samples_path) as f:
            samples_config = json.load(f)
        with open(sector_path) as f:
            sector_config = json.load(f)
        with open(tags_path) as f:
            tags_config = json.load(f)
        with open(news_path) as f:
            news_config = json.load(f)

        load_etf_samples(conn, samples_config["etfs"])
        load_sector_mapping(conn, sector_config["mapping"])
        load_mock_news(conn, news_config["news"])

        etf_list = get_active_etf_samples(conn)

        # 3. 为每个ETF生成/获取日线数据并计算因子
        all_daily_records = []
        heat_factors = {}
        momentum_factors = {}
        liquidity_factors = {}
        lowvol_factors = {}
        momentum_medians = {}

        for etf in etf_list:
            code = etf["code"]
            try:
                # 生成Mock日线数据并写入
                daily_records = generate_mock_daily_data(code, target_date, 22)
                all_daily_records.extend(daily_records)
            except Exception as e:
                errors.append({"etf_code": code, "error": str(e), "stage": "daily_data"})
                continue

        upsert_daily_data(conn, all_daily_records)

        # 4. 计算各因子
        factor_records = []
        for etf in etf_list:
            code = etf["code"]
            try:
                daily_rows = get_daily_data_window(conn, code, target_date, 22)
                if len(daily_rows) < 6:
                    errors.append({"etf_code": code, "error": "数据不足(需要至少6日)", "stage": "data_window"})
                    continue

                close_prices = [r["close_price"] for r in daily_rows]
                turnovers = [r["turnover"] for r in daily_rows]
                sousuo_uvs = [r["sousuo_uv"] for r in daily_rows]
                sousuo_click_uvs = [r["sousuo_click_uv"] for r in daily_rows]
                fenshi_uvs = [r["fenshi_uv"] for r in daily_rows]
                add_uvs = [r["add_uv"] for r in daily_rows]
                buy_uvs = [r["buy_uv"] for r in daily_rows]

                # 热度因子
                heat_result = calc_heat_factor(
                    sousuo_uvs, sousuo_click_uvs, fenshi_uvs, add_uvs, buy_uvs
                )
                # 动量因子
                momentum = calc_momentum_factor(close_prices)
                # 流动性因子
                liquidity = calc_liquidity_factor(turnovers)
                # 低波因子
                lowvol = calc_lowvol_factor(close_prices)
                # 20日动量中位数(用于标签)
                mm_20d = calc_20d_momentum_median(close_prices)

                if heat_result:
                    heat_factors[code] = heat_result["heat_factor"]
                else:
                    heat_factors[code] = None

                momentum_factors[code] = momentum
                liquidity_factors[code] = liquidity
                lowvol_factors[code] = lowvol
                momentum_medians[code] = mm_20d

                factor_records.append((
                    code, target_date,
                    heat_result["search_heat_z"] if heat_result else None,
                    heat_result["first_buy_heat_z"] if heat_result else None,
                    heat_result["heat_factor"] if heat_result else None,
                    momentum, liquidity, lowvol,
                ))
            except Exception as e:
                errors.append({"etf_code": code, "error": str(e), "stage": "factor_calc"})
                heat_factors[code] = None
                momentum_factors[code] = None
                liquidity_factors[code] = None
                lowvol_factors[code] = None
                momentum_medians[code] = None

        upsert_factors(conn, factor_records)

        # 5. 计算排名与综合评分
        rankings = compute_all_rankings(
            heat_factors, momentum_factors, liquidity_factors, lowvol_factors
        )

        ranking_records = []
        history_records = []
        for code, data in rankings.items():
            ranking_records.append((
                code, target_date,
                data["heat_rank"], data["momentum_rank"],
                data["liquidity_rank"], data["lowvol_rank"],
                data["heat_rank_score"], data["momentum_rank_score"],
                data["liquidity_rank_score"], data["lowvol_rank_score"],
                data["composite_score"], data["overall_rank"],
            ))
            history_records.append((
                target_date, code, data["composite_score"], data["overall_rank"],
            ))

        upsert_rankings(conn, ranking_records)
        insert_history_scores(conn, history_records)

        # 6. 计算标签
        label_records = []
        for code in [e["code"] for e in etf_list]:
            tag = calc_market_tag(momentum_medians.get(code))
            mock_tags = get_mock_fund_tags(code, tags_config.get("etf_tags", {}))
            label_records.append((
                code, target_date, tag,
                momentum_medians.get(code),
                json.dumps(mock_tags, ensure_ascii=False) if mock_tags else "[]",
            ))
        upsert_labels(conn, label_records)

        # 7. 刷新缓存
        cache.invalidate()

        # 8. 获取Top5
        from src.data.models.data_access import get_top_n_rankings
        top5 = get_top_n_rankings(conn, target_date, 5)

        return {
            "status": "COMPLETED",
            "date": target_date,
            "etf_count": len(etf_list),
            "top5": top5,
            "errors": errors,
        }

    finally:
        conn.close()


if __name__ == "__main__":
    result = run_daily_job()
    print(f"Status: {result['status']}")
    print(f"Date: {result['date']}")
    print(f"ETFs calculated: {result['etf_count']}")
    print(f"Top 5:")
    for i, etf in enumerate(result['top5'], 1):
        print(f"  #{i}: {etf['etf_code']} {etf.get('etf_name','')} score={etf['composite_score']} rank={etf['overall_rank']}")
    if result['errors']:
        print(f"Errors: {len(result['errors'])}")
