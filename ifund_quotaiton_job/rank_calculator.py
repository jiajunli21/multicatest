"""榜单排序计算层。

负责 4 维度 × 前9/后9 = 8 份榜单的排序和领涨成分股计算。
"""

import logging
from typing import Optional

from . import config
from .data_fetcher import fetch_all_market_stock_changes

logger = logging.getLogger(__name__)


def _get_safe_float(value, default: float = 0.0) -> float:
    """安全获取浮点值，用于排序。缺失、None 或不可转换时返回 default。"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _sort_etf_list(
    etf_list: list[dict],
    field: str,
    descending: bool = True,
) -> list[dict]:
    """按指定字段排序 ETF 列表。

    Args:
        etf_list: ETF 列表，每项为 dict
        field: 排序字段名
        descending: True=DESC(从大到小), False=ASC(从小到大)

    Returns:
        排序后的 ETF 列表
    """
    return sorted(
        etf_list,
        key=lambda x: _get_safe_float(x.get(field), 0.0),
        reverse=descending,
    )


def _build_rank_entry(etf: dict, dimension: str) -> dict:
    """构建单个榜单条目。"""
    return {
        "code": etf.get("code", etf.get("stockCode", "")),
        "name": etf.get("name", etf.get("stockName", "")),
        dimension: etf.get(dimension, None),
        "topLeadStockCode": etf.get("topLeadStockCode", ""),
        "topLeadStockName": etf.get("topLeadStockName", ""),
        "topLeadStockChangeRatio": etf.get("topLeadStockChangeRatio", None),
        "bottomLeadStockCode": etf.get("bottomLeadStockCode", ""),
        "bottomLeadStockName": etf.get("bottomLeadStockName", ""),
        "bottomLeadStockChangeRatio": etf.get("bottomLeadStockChangeRatio", None),
    }


def _compute_lead_stocks(
    etf_list: list[dict],
    component_relations: Optional[dict[str, list[dict]]],
    all_market_changes: Optional[dict[str, dict]],
) -> list[dict]:
    """计算领涨/领跌成分股。

    对每只入榜 ETF：
    1. 从 component_relations 获取该 ETF 的过滤后成分股列表
    2. 从 all_market_changes 获取这些成分股的涨幅
    3. 按涨幅排序取前 9 第一只(topLead)、后 9 第一只(bottomLead)

    降级规则：
    - component_relations 为 None：所有领涨/领跌字段置空
    - all_market_changes 为 None：所有领涨/领跌字段置空
    """
    if component_relations is None or all_market_changes is None:
        for etf in etf_list:
            etf["topLeadStockCode"] = ""
            etf["topLeadStockName"] = ""
            etf["topLeadStockChangeRatio"] = None
            etf["bottomLeadStockCode"] = ""
            etf["bottomLeadStockName"] = ""
            etf["bottomLeadStockChangeRatio"] = None
        return etf_list

    for etf in etf_list:
        code = etf.get("code", etf.get("stockCode", ""))
        components = component_relations.get(code, [])

        if not components:
            etf["topLeadStockCode"] = ""
            etf["topLeadStockName"] = ""
            etf["topLeadStockChangeRatio"] = None
            etf["bottomLeadStockCode"] = ""
            etf["bottomLeadStockName"] = ""
            etf["bottomLeadStockChangeRatio"] = None
            continue

        # 为成分股附加上涨幅数据
        enriched = []
        for comp in components:
            comp_code = comp.get("code", comp.get("stockCode", ""))
            market_data = all_market_changes.get(comp_code, {})
            comp_chgpct = _get_safe_float(
                market_data.get("chgpct", comp.get("chgpct", comp.get("changeRatio", 0.0)))
            )
            enriched.append({
                "code": comp_code,
                "name": comp.get("name", comp.get("stockName", "")),
                "chgpct": comp_chgpct,
            })

        # 按涨幅降序排序，取前9取第一只（领涨）
        sorted_desc = sorted(enriched, key=lambda x: x["chgpct"], reverse=True)
        if sorted_desc:
            top = sorted_desc[0]
            etf["topLeadStockCode"] = top["code"]
            etf["topLeadStockName"] = top["name"]
            etf["topLeadStockChangeRatio"] = top["chgpct"]

        # 按涨幅升序排序，取前9取第一只（领跌）
        sorted_asc = sorted(enriched, key=lambda x: x["chgpct"])
        if sorted_asc:
            bottom = sorted_asc[0]
            etf["bottomLeadStockCode"] = bottom["code"]
            etf["bottomLeadStockName"] = bottom["name"]
            etf["bottomLeadStockChangeRatio"] = bottom["chgpct"]

    return etf_list


def calculate_rankings(
    etf_list: list[dict],
    quotes: dict[str, dict],
    component_relations: Optional[dict[str, list[dict]]],
    all_market_changes: Optional[dict[str, dict]],
    base_url: str = "",
) -> dict[str, list[dict]]:
    """计算 4 维度 × 前9/后9 = 8 份榜单。

    Args:
        etf_list: ETF 基本信息列表
        quotes: 扶摇行情数据，key=stockCode, value=行情fields
        component_relations: 成分股关系（可为 None）
        all_market_changes: 全市场股票涨幅（可为 None）
        base_url: API 基地址

    Returns:
        8 份榜单的 dict:
        {
            "changeRatioTop9": [...],
            "changeRatioBottom9": [...],
            "speedRatioTop9": [...],
            "speedRatioBottom9": [...],
            "volumeRatioTop9": [...],
            "volumeRatioBottom9": [...],
            "limitUpCountTop9": [...],
            "limitUpCountBottom9": [...],
        }
    """
    # 为每个 ETF 附加行情数据
    enriched = []
    for etf in etf_list:
        code = etf.get("code", etf.get("stockCode", ""))
        q = quotes.get(code, {})
        item = {
            "code": code,
            "name": etf.get("name", etf.get("stockName", "")),
            "chgpct": _get_safe_float(q.get("chgpct", q.get("changeRatio"))),
            "speedRatio": (
                _get_safe_float(q.get("speedRatio"))
                if config.SPEED_RATIO_FETCH_ENABLED
                else config.MOCK_SPEED_RATIO
            ),
            "volumeRatio": (
                _get_safe_float(q.get("volumeRatio"), 1.0)
                if config.VOLUME_RATIO_FETCH_ENABLED
                else config.MOCK_VOLUME_RATIO
            ),
            "etfLimitUpStockCnt": _get_safe_float(q.get("etfLimitUpStockCnt", q.get("limitUpCount"))),
            "topLeadStockCode": "",
            "topLeadStockName": "",
            "topLeadStockChangeRatio": None,
            "bottomLeadStockCode": "",
            "bottomLeadStockName": "",
            "bottomLeadStockChangeRatio": None,
        }
        enriched.append(item)

    # 计算领涨/领跌成分股
    enriched = _compute_lead_stocks(enriched, component_relations, all_market_changes)

    # 按 4 维度分别排序并取前9/后9
    result = {}

    dimensions = [
        ("changeRatio", "chgpct"),
        ("speedRatio", "speedRatio"),
        ("volumeRatio", "volumeRatio"),
        ("limitUpCount", "etfLimitUpStockCnt"),
    ]

    for dim_key, sort_field in dimensions:
        # 降序(前9): 值最大的前 N 只
        desc_sorted = _sort_etf_list(enriched, sort_field, descending=True)
        top9 = desc_sorted[: config.TOP_N]
        result[f"{dim_key}Top9"] = [_build_rank_entry(e, sort_field) for e in top9]

        # 升序(后9): 值最小的前 N 只
        asc_sorted = _sort_etf_list(enriched, sort_field, descending=False)
        bottom9 = asc_sorted[: config.BOTTOM_N]
        result[f"{dim_key}Bottom9"] = [_build_rank_entry(e, sort_field) for e in bottom9]

    return result
