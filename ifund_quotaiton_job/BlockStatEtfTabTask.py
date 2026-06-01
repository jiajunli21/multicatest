"""BlockStatEtfTabTask — ETF 板块统计定时任务。

唯一计算入口：BlockStatEtfTabTask.execute()
唯一数据存储：Redis key plateStatEtf:rank:data（8 份榜单 JSON）

执行流程：
1. 拉取基金池 ETF 列表
2. 拉取扶摇 ETF 行情（chgpct + etfLimitUpStockCnt）
3. 拉取成分股关系（按 market 17/33/177 过滤）
4. 拉取三市场全量股票涨幅（待接口确认，当前降级）
5. 4 维度排序取前9/后9 → 8 份榜单
6. 计算领涨/领跌成分股
7. 组装 JSON 写入 Redis

降级规则：
- 基金池返回空：本次不覆盖 Redis 老数据
- 扶摇查询失败：本次不覆盖 Redis 老数据
- 成分股接口失败：允许只写榜单主数据，领涨成分股字段置空
- 三市场全量涨幅拉取失败：允许只写榜单主数据，成分股字段置空
"""

import logging
import time
from typing import Optional

from . import config
from .data_fetcher import (
    fetch_fund_pool_etf_list,
    fetch_fuyao_etf_quotes,
    fetch_component_stocks,
    fetch_all_market_stock_changes,
)
from .rank_calculator import calculate_rankings
from .redis_writer import write_rank_data, read_rank_data

logger = logging.getLogger(__name__)


class BlockStatEtfTabTask:
    """ETF 板块统计定时任务。

    Cron 表达式（每分钟执行一次）由调度框架注入，本类只负责 execute() 业务逻辑。
    """

    def __init__(self, api_base_url: str = ""):
        self.api_base_url = api_base_url

    def execute(self) -> dict:
        """执行一次完整的榜单刷新周期。

        Returns:
            {
                "success": bool,
                "rankings_written": bool,
                "errors": list[str],
                "degraded": bool,
                "update_time": int,
            }
        """
        errors = []
        degraded = False
        start = time.time()

        # ---- Step 1: 拉取基金池 ETF 列表 ----
        etf_list, err = fetch_fund_pool_etf_list(self.api_base_url)
        if err:
            errors.append(f"fund_pool: {err}")
            logger.error("基金池拉取失败，本次不覆盖 Redis 老数据。err=%s", err)
            return {
                "success": False,
                "rankings_written": False,
                "errors": errors,
                "degraded": False,
                "update_time": int(start),
            }
        if not etf_list:
            logger.warning("基金池返回空列表，本次不覆盖 Redis 老数据")
            return {
                "success": True,
                "rankings_written": False,
                "errors": [],
                "degraded": False,
                "update_time": int(start),
            }

        stock_codes = [
            item.get("code", item.get("stockCode", ""))
            for item in etf_list
            if item.get("code") or item.get("stockCode")
        ]
        logger.info("基金池 ETF 数量: %d", len(stock_codes))

        # ---- Step 2: 拉取扶摇 ETF 行情 ----
        quotes, err = fetch_fuyao_etf_quotes(self.api_base_url, stock_codes)
        if err:
            errors.append(f"fuyao_quotes: {err}")
            logger.error("扶摇行情拉取失败，本次不覆盖 Redis 老数据。err=%s", err)
            return {
                "success": False,
                "rankings_written": False,
                "errors": errors,
                "degraded": False,
                "update_time": int(start),
            }
        if quotes is None:
            errors.append("fuyao_quotes: returned None")
            return {
                "success": False,
                "rankings_written": False,
                "errors": errors,
                "degraded": False,
                "update_time": int(start),
            }

        logger.info("扶摇行情 ETF 数量: %d", len(quotes))

        # ---- Step 3: 拉取成分股关系 ----
        component_relations, comp_err = fetch_component_stocks(self.api_base_url, stock_codes)
        if comp_err:
            errors.append(f"component_stocks: {comp_err}")
            degraded = True
            component_relations = None
            logger.warning("成分股关系拉取失败（降级：领涨成分股置空）")

        # ---- Step 4: 拉取三市场全量股票涨幅 ----
        all_market_changes, mkt_err = fetch_all_market_stock_changes(self.api_base_url)
        if mkt_err:
            errors.append(f"all_market_stocks: {mkt_err}")
            degraded = True
            all_market_changes = None
            logger.warning("三市场全量涨幅拉取失败/未启用（降级：成分股字段置空）")

        # ---- Step 5-6: 计算排名 + 领涨成分股 ----
        rankings = calculate_rankings(
            etf_list=etf_list,
            quotes=quotes,
            component_relations=component_relations,
            all_market_changes=all_market_changes,
            base_url=self.api_base_url,
        )

        # ---- Step 7: 写入 Redis ----
        written = write_rank_data(rankings)

        elapsed_ms = int((time.time() - start) * 1000)
        result = {
            "success": written,
            "rankings_written": written,
            "errors": errors,
            "degraded": degraded,
            "update_time": int(start),
            "elapsed_ms": elapsed_ms,
        }

        if written:
            logger.info(
                "BlockStatEtfTabTask 执行完成: etf_count=%d, rankings_written=True, "
                "degraded=%s, elapsed_ms=%d",
                len(stock_codes),
                degraded,
                elapsed_ms,
            )
        else:
            logger.error("BlockStatEtfTabTask Redis 写入失败")

        return result


def run_task(api_base_url: str = "") -> dict:
    """便捷入口：创建任务实例并执行。"""
    task = BlockStatEtfTabTask(api_base_url=api_base_url)
    return task.execute()
