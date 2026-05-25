"""定时任务编排模块。

Status: [default]

编排每日 ETF 早盘评分计算流程：
1. 生成/读取 Mock 数据
2. 四因子计算
3. 排名 + 综合评分
4. 标签计算
5. 落库 + 缓存
"""

import logging
from datetime import date, datetime
from typing import Optional

from .config import (
    Z_SCORE_WINDOW,
    LIQUIDITY_WINDOW,
    LOW_VOL_PRICE_WINDOW,
)
from .models import CalcStatus, ETFInfo, HistoricalRecord, MarketTag, Top5Result
from .data.mock_data import (
    generate_etf_infos,
    generate_heat_raw_fields_window,
    generate_price_series,
    generate_turnover_series,
)
from .data.repository import (
    init_db,
    save_etf_scores,
    save_historical_records,
    get_etf_scores,
    get_top5_scores,
)
from .calc.heat import calc_heat_factor_for_etf
from .calc.momentum import calc_momentum_factor
from .calc.liquidity import calc_liquidity_factor
from .calc.low_vol import calc_low_vol_factor
from .calc.ranking import calc_rank_scores
from .calc.scoring import calc_composite_scores, build_top5_result
from .calc.tags import calc_market_tag, get_etf_tags
from . import cache

logger = logging.getLogger(__name__)


def run_daily_calculation(calc_date: Optional[date] = None) -> Top5Result:
    """执行每日 ETF 早盘评分全流程计算。

    Args:
        calc_date: 计算日期 (T 日)，默认今天

    Returns:
        Top5Result

    幂等性 [default]:
    - 重复运行同一天会覆盖之前的落库结果（INSERT OR REPLACE）
    - 缓存会刷新
    """
    if calc_date is None:
        calc_date = date.today()

    logger.info(f"=== 早盘宝每日计算开始: {calc_date.isoformat()} ===")

    # Step 0: 初始化数据库
    init_db()

    # Step 1: 获取 ETF 计算样本 [mock]
    etf_infos = generate_etf_infos()
    etf_codes = [e.code for e in etf_infos]
    etf_name_map = {e.code: e.name for e in etf_infos}
    logger.info(f"ETF 样本数: {len(etf_infos)} [mock]")

    # Step 2: 生成 Mock 数据（热度原始字段 + 行情数据 + 成交额）
    logger.info("生成 Mock 数据...")
    heat_data: dict[str, list] = {}
    price_data: dict[str, list] = {}

    for etf in etf_infos:
        # 热度原始字段 (T-19 ~ T)
        heat_data[etf.code] = generate_heat_raw_fields_window(
            etf.code, calc_date, window=Z_SCORE_WINDOW
        )
        # 行情数据（价格序列，需要 LOW_VOL_PRICE_WINDOW 个交易日）
        prices = generate_price_series(
            etf.code, calc_date, window=LOW_VOL_PRICE_WINDOW
        )
        # 填充 Mock 成交额
        prices = generate_turnover_series(etf.code, prices)
        price_data[etf.code] = prices

    # Step 3: 四因子计算
    logger.info("计算热度因子... [mock]")
    heat_results = {}
    for etf in etf_infos:
        heat_results[etf.code] = calc_heat_factor_for_etf(
            etf.code, calc_date, heat_data[etf.code]
        )

    logger.info("计算动量因子... [default]")
    momentum_results = {}
    for etf in etf_infos:
        momentum_results[etf.code] = calc_momentum_factor(
            etf.code, calc_date, price_data[etf.code]
        )

    logger.info("计算流动性因子... [default]")
    liquidity_results = {}
    for etf in etf_infos:
        liquidity_results[etf.code] = calc_liquidity_factor(
            etf.code, calc_date, price_data[etf.code],
            window=LIQUIDITY_WINDOW,
        )

    logger.info("计算低波因子... [default]")
    low_vol_results = {}
    for etf in etf_infos:
        low_vol_results[etf.code] = calc_low_vol_factor(
            etf.code, calc_date, price_data[etf.code],
        )

    # Step 4: 排名计算
    logger.info("计算排名分数... [default]")

    heat_ranks = calc_rank_scores(
        [(code, r.heat_factor, r.status) for code, r in heat_results.items()],
        descending=True,
    )
    momentum_ranks = calc_rank_scores(
        [(code, r.momentum_factor, r.status) for code, r in momentum_results.items()],
        descending=True,
    )
    liquidity_ranks = calc_rank_scores(
        [(code, r.avg_turnover_20d, r.status) for code, r in liquidity_results.items()],
        descending=True,
    )
    low_vol_ranks = calc_rank_scores(
        [(code, r.low_vol_factor, r.status) for code, r in low_vol_results.items()],
        descending=False,  # ASC — 低波越小越好
    )

    # Step 5: 大盘标签 [default]
    logger.info("计算大盘标签... [default]")
    price_series_list = [(code, price_data[code]) for code in etf_codes]
    market_tag = calc_market_tag(price_series_list, calc_date)

    # Step 6: ETF 综合评分
    logger.info("计算 ETF 综合评分... [default]")
    scores = calc_composite_scores(
        heat_ranks, momentum_ranks, liquidity_ranks, low_vol_ranks,
        calc_date, etf_name_map, market_tag,
    )

    # Step 7: 落库
    logger.info("保存评分结果到数据库... [default]")
    save_etf_scores(scores)

    # Step 8: 历史记录落库（Top5）
    historical = []
    for s in scores[:5]:
        historical.append(HistoricalRecord(
            date=calc_date,
            etf_code=s.etf_code,
            etf_name=s.etf_name,
            composite_score=s.composite_score,
            rank=s.rank,
            signal_3d_return=None,  # 需后续计算，T+3 才有
            current_return=None,
        ))
    save_historical_records(historical)

    # Step 9: 构建 Top5 结果
    top5 = build_top5_result(
        scores, calc_date, market_tag, len(etf_infos),
    )

    # Step 10: 缓存
    cache.cache_etf_scores(calc_date, scores)
    cache.cache_top5(calc_date, top5)

    # Step 11: 日志输出统计
    calculable_count = sum(1 for s in scores if s.status != CalcStatus.NOT_CALCULABLE)
    logger.info(f"=== 计算完成: {calculable_count}/{len(scores)} 可计算, "
                 f"大盘标签: {market_tag.value} ===")

    return top5


def get_latest_result(calc_date: Optional[date] = None) -> Top5Result:
    """获取最新计算结果（优先缓存，其次数据库）。"""
    if calc_date is None:
        calc_date = date.today()

    # 查缓存
    cached = cache.get_cached_top5(calc_date)
    if cached:
        logger.info(f"命中缓存: {calc_date.isoformat()}")
        return cached

    # 查数据库
    top5_records = get_top5_scores(calc_date)
    if top5_records:
        logger.info(f"从数据库加载: {calc_date.isoformat()}")
        # 重建 Top5Result
        from .models import ETFScore, MarketTag
        scores = []
        for r in top5_records:
            s = ETFScore(
                etf_code=r["etf_code"],
                etf_name=r["etf_name"],
                calc_date=date.fromisoformat(r["calc_date"]),
                heat_rank_score=r["heat_rank_score"],
                momentum_rank_score=r["momentum_rank_score"],
                liquidity_rank_score=r["liquidity_rank_score"],
                low_vol_rank_score=r["low_vol_rank_score"],
                composite_score=r["composite_score"],
                rank=r["rank"],
                sector=r.get("sector", ""),
                tags=r.get("tags", []),
                market_tag=MarketTag(r["market_tag"]) if r.get("market_tag") else None,
                status=CalcStatus(r.get("status", "success")),
            )
            scores.append(s)

        from .data.repository import get_etf_scores
        all_records = get_etf_scores(calc_date)

        from .calc.tags import calc_market_tag
        from .data.mock_data import generate_price_series, generate_turnover_series
        etf_infos = generate_etf_infos()
        price_series_list = []
        for e in etf_infos:
            prices = generate_price_series(e.code, calc_date, window=22)
            prices = generate_turnover_series(e.code, prices)
            price_series_list.append((e.code, prices))
        market_tag = calc_market_tag(price_series_list, calc_date)

        top5 = build_top5_result(
            scores, calc_date, market_tag, len(all_records),
        )

        cache.cache_top5(calc_date, top5)
        return top5

    # 无数据，执行计算
    logger.info(f"无缓存和数据库数据，触发计算: {calc_date.isoformat()}")
    return run_daily_calculation(calc_date)
