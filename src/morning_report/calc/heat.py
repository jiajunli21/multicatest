"""热度因子计算模块。

Status: [mock] — 热度原始字段 (sousuo_uv等) fund-indic-search-test 全部 NO_MATCH.

公式：
- T日搜索热度 = log(1 + sousuo_uv + 3 * sousuo_click_uv)
- T日首购热度 = log(1 + fenshi_uv + 5 * add_uv + 20 * buy_uv)
- 搜索热度Z分数 = (T日值 - 均值) / 标准差
- 首购热度Z分数 = (T日值 - 均值) / 标准差
- 热度因子 = 0.55 * 搜索热度Z分数 + 0.45 * 首购热度Z分数
"""

import math
from datetime import date
from typing import Optional

from ..config import (
    HEAT_SEARCH_WEIGHT,
    HEAT_BUY_WEIGHT,
    Z_SCORE_WINDOW,
)
from ..models import CalcStatus, DataSource, HeatFactorResult, HeatRawFields


def calc_search_heat(sousuo_uv: float, sousuo_click_uv: float) -> float:
    """计算搜索热度 = log(1 + sousuo_uv + 3 * sousuo_click_uv)."""
    return math.log1p(sousuo_uv + 3.0 * sousuo_click_uv)


def calc_buy_heat(fenshi_uv: float, add_uv: float, buy_uv: float) -> float:
    """计算首购热度 = log(1 + fenshi_uv + 5 * add_uv + 20 * buy_uv)."""
    return math.log1p(fenshi_uv + 5.0 * add_uv + 20.0 * buy_uv)


def calc_z_score(value: float, values: list[float]) -> float:
    """计算 Z 分数 = (value - mean) / std.

    边界规则 [default]:
    - 标准差 = 0 时 Z 分数记为 0
    - values 为空时 Z 分数记为 0
    """
    if not values or len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(variance)

    if std == 0.0:
        return 0.0

    return (value - mean) / std


def calc_heat_factor_for_etf(
    etf_code: str,
    calc_date: date,
    raw_fields_window: list[HeatRawFields],
) -> HeatFactorResult:
    """计算单个 ETF 的热度因子。

    Args:
        etf_code: ETF 代码
        calc_date: 计算日期 (T 日)
        raw_fields_window: 从 T-19 到 T 日的热度原始字段序列（20个交易日）

    Returns:
        HeatFactorResult
    """
    if not raw_fields_window:
        return HeatFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            search_heat_t=0.0,
            buy_heat_t=0.0,
            search_heat_z=0.0,
            buy_heat_z=0.0,
            heat_factor=0.0,
            status=CalcStatus.NOT_CALCULABLE,
        )

    # 找出 T 日数据
    t_day_fields = raw_fields_window[-1]

    # 计算搜索热度序列（整个窗口）
    search_heat_series = [
        calc_search_heat(f.sousuo_uv, f.sousuo_click_uv)
        for f in raw_fields_window
    ]

    # 计算首购热度序列
    buy_heat_series = [
        calc_buy_heat(f.fenshi_uv, f.add_uv, f.buy_uv)
        for f in raw_fields_window
    ]

    # T 日值
    search_heat_t = search_heat_series[-1]
    buy_heat_t = buy_heat_series[-1]

    # Z 分数
    search_heat_z = calc_z_score(search_heat_t, search_heat_series)
    buy_heat_z = calc_z_score(buy_heat_t, buy_heat_series)

    # 热度因子
    heat_factor = HEAT_SEARCH_WEIGHT * search_heat_z + HEAT_BUY_WEIGHT * buy_heat_z

    # 检查缺失值
    status = CalcStatus.SUCCESS
    t_fields = raw_fields_window[-1]
    has_missing = any(
        getattr(t_fields, attr, 0) == 0
        for attr in ["sousuo_uv", "fenshi_uv", "add_uv", "buy_uv"]
    )

    return HeatFactorResult(
        etf_code=etf_code,
        calc_date=calc_date,
        search_heat_t=round(search_heat_t, 6),
        buy_heat_t=round(buy_heat_t, 6),
        search_heat_z=round(search_heat_z, 6),
        buy_heat_z=round(buy_heat_z, 6),
        heat_factor=round(heat_factor, 6),
        status=status,
        source=DataSource.MOCK,
    )
