"""标签计算模块。

Status: [default] for market tag, [mock] for individual ETF tags.

公式 [default]:
- 20日动量 = C_t / C_t-20 - 1
- 20日动量中位数 < -0.03 → "谨慎参与"，否则 "积极参与"
"""

from datetime import date, timedelta
from typing import Optional

from ..config import MARKET_TAG_THRESHOLD, MOCK_ETF_TAGS, MOCK_DEFAULT_TAGS
from ..models import CalcStatus, DailyPrice, MarketTag


def calc_market_tag(
    price_series_list: list[tuple[str, list[DailyPrice]]],
    calc_date: date,
) -> MarketTag:
    """计算大盘标签：基于所有 ETF 的 20 日动量中位数.

    边界规则 [default]:
    - 可计算 ETF 不足 3 个 → 默认 "积极参与"
    - 20 日动量中位数 < -0.03 → "谨慎参与"
    - 否则 → "积极参与"

    Args:
        price_series_list: [(etf_code, price_series), ...] 所有 ETF 的价格序列
        calc_date: 计算日期
    """
    momentum_20d_list = []

    for etf_code, price_series in price_series_list:
        momentum = _calc_20d_momentum(price_series, calc_date)
        if momentum is not None:
            momentum_20d_list.append(momentum)

    if len(momentum_20d_list) < 3:
        return MarketTag.ACTIVE

    momentum_20d_list.sort()
    n = len(momentum_20d_list)
    if n % 2 == 1:
        median = momentum_20d_list[n // 2]
    else:
        median = (momentum_20d_list[n // 2 - 1] + momentum_20d_list[n // 2]) / 2.0

    if median < MARKET_TAG_THRESHOLD:
        return MarketTag.CAUTIOUS
    return MarketTag.ACTIVE


def _calc_20d_momentum(
    price_series: list[DailyPrice],
    calc_date: date,
) -> Optional[float]:
    """计算单个 ETF 的 20 日动量 = C_t / C_t-20 - 1."""
    if not price_series:
        return None

    price_map = {p.date: p.close_price for p in price_series if p.close_price > 0}

    # 查找 T 日和 T-20 日最近可用收盘价
    c_t = _find_nearest(calc_date, price_map, 3)
    c_t_minus_20 = _find_nearest(calc_date - timedelta(days=20), price_map, 5)

    if c_t is None or c_t_minus_20 is None or c_t_minus_20 == 0.0:
        return None

    return c_t / c_t_minus_20 - 1.0


def _find_nearest(
    target: date,
    price_map: dict[date, float],
    lookback: int,
) -> Optional[float]:
    for i in range(lookback + 1):
        d = target - timedelta(days=i)
        if d in price_map and price_map[d] > 0:
            return price_map[d]
    return None


def get_etf_tags(etf_code: str) -> list[str]:
    """获取个基标签 [mock].

    本轮使用静态 Mock 标签，后续替换为 AI 生成标签。
    """
    return MOCK_ETF_TAGS.get(etf_code, list(MOCK_DEFAULT_TAGS))
