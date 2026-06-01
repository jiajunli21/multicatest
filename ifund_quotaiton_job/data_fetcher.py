"""数据拉取层：基金池、扶摇行情、成分股关系、全量股票涨幅。

外部接口均为 stub/骨架实现，等待真实接口确认后接入。
所有 fetcher 方法统一返回 (data, error) 元组。
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional

from . import config

logger = logging.getLogger(__name__)


def _http_post(url: str, body: dict, timeout: int = 10) -> tuple[Optional[dict], Optional[str]]:
    """通用 HTTP POST 请求，返回 (response_dict, error)。"""
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.URLError as e:
        return None, f"HTTP request failed: {e.reason}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def fetch_fund_pool_etf_list(base_url: str) -> tuple[Optional[list[dict]], Optional[str]]:
    """拉取行业主题 ETF 列表。

    POST /quotation/fund_pool/v2/query
    body: {"uniqueType": "etf_third_level_track_list"}

    Returns:
        (etf_list, error): etf_list 为 ETF 基本信息列表，每项含 stockCode/stockName。
        返回空列表时本次不覆盖 Redis 老数据。
    """
    body = {"uniqueType": config.FUND_POOL_UNIQUE_TYPE}

    try:
        data, err = _http_post(base_url + config.FUND_POOL_URL, body)
    except Exception:
        data, err = None, "fund_pool request exception"

    if err:
        logger.warning("基金池接口失败: %s", err)
        return None, err

    if not data or not isinstance(data, dict):
        return None, "fund_pool returned empty or invalid response"

    etf_list = data.get("data", data.get("list", []))
    if isinstance(etf_list, list):
        return etf_list, None

    return [], None


def fetch_fuyao_etf_quotes(base_url: str, stock_codes: list[str]) -> tuple[Optional[dict[str, dict]], Optional[str]]:
    """拉取扶摇 ETF 行情数据（涨幅 + 涨停数）。

    POST /quotation/data/query/v1/table
    body: {"codes": [...], "indexIds": ["chgpct", "etfLimitUpStockCnt"]}

    Returns:
        (quotes_by_code, error): key 为 stockCode，value 为行情字段 dict。
        失败时返回 None，本次不覆盖 Redis 老数据。
    """
    if not stock_codes:
        return {}, None

    body = {
        "codes": stock_codes,
        "indexIds": ["chgpct", "etfLimitUpStockCnt"],
    }

    try:
        data, err = _http_post(base_url + config.FUYAO_ETF_QUOTE_URL, body)
    except Exception:
        data, err = None, "fuyao_etf_quote request exception"

    if err:
        logger.warning("扶摇 ETF 行情接口失败: %s", err)
        return None, err

    if not data or not isinstance(data, dict):
        return None, "fuyao_etf_quote returned empty or invalid response"

    raw = data.get("data", data)
    if isinstance(raw, list):
        result = {}
        for item in raw:
            code = item.get("code", item.get("stockCode", ""))
            if code:
                result[code] = item
        return result, None

    return {}, None


def fetch_component_stocks(
    base_url: str, stock_codes: list[str]
) -> tuple[Optional[dict[str, list[dict]]], Optional[str]]:
    """拉取成分股关系。

    POST /quotation/data/query/v1/relation
    body: {"codes": [...], "relationship": "stock_etf_subred"}

    按 market 17/33/177 过滤成分股。

    Returns:
        (relations_by_code, error): key 为 ETF code，value 为过滤后的成分股列表。
        失败时允许只写榜单主数据，领涨成分股字段置空。
    """
    if not stock_codes:
        return {}, None

    body = {
        "codes": stock_codes,
        "relationship": config.STOCK_RELATION_TYPE,
    }

    try:
        data, err = _http_post(base_url + config.STOCK_RELATION_URL, body)
    except Exception:
        data, err = None, "component_stock request exception"

    if err:
        logger.warning("成分股关系接口失败（降级：领涨成分股置空）: %s", err)
        return None, err

    if not data or not isinstance(data, dict):
        return None, "component_stock returned empty or invalid response"

    raw = data.get("data", data)
    result = {}
    if isinstance(raw, list):
        for item in raw:
            code = item.get("code", item.get("stockCode", ""))
            stocks = item.get("stocks", item.get("components", []))
            # 按市场 17/33/177 过滤
            filtered = [
                s for s in stocks
                if s.get("market") in config.MARKET_FILTER
            ]
            if code:
                result[code] = filtered
    elif isinstance(raw, dict):
        for code, item in raw.items():
            stocks = item.get("stocks", item.get("components", []))
            result[code] = [
                s for s in stocks
                if s.get("market") in config.MARKET_FILTER
            ]

    return result, None


def fetch_all_market_stock_changes(base_url: str) -> tuple[Optional[dict[str, dict]], Optional[str]]:
    """拉取三市场全量股票涨幅。

    接口路径待确认，当前由 ALL_MARKET_STOCK_FETCH_ENABLED 控制。
    失败时允许领涨成分股字段置空。

    Returns:
        (changes_by_code, error): key 为 stockCode，value 含 chgpct 涨幅字段。
    """
    if not config.ALL_MARKET_STOCK_FETCH_ENABLED:
        return None, "ALL_MARKET_STOCK_FETCH_ENABLED is False"

    try:
        data, err = _http_post(base_url + config.ALL_MARKET_STOCK_URL, {"type": "all"})
    except Exception:
        data, err = None, "all_market_stock request exception"

    if err:
        logger.warning("三市场全量股票涨幅接口失败（降级：领涨成分股置空）: %s", err)
        return None, err

    if not data or not isinstance(data, dict):
        return None, "all_market_stock returned empty or invalid response"

    raw = data.get("data", data)
    result = {}
    if isinstance(raw, list):
        for item in raw:
            code = item.get("code", item.get("stockCode", ""))
            if code:
                result[code] = item
    return result, None
