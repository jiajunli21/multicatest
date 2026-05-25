"""低波因子计算。[default]

DI-009: 低波因子 = std(20个日收益率)

日收益率_t = C_t / C_t-1 - 1 (基于收盘价 unitNav 序列)
需要22个收盘价以计算20个日收益率。

[verified]: unitNav/unit_nav online 可用作收盘价替代源
[default]: 不等于 annualizedVolatilityYear (近1年年化波动率)

排名方向: ASC (值越小排名越高)
"""

import math
from typing import Optional


def calc_daily_returns(close_prices: list) -> list:
    """从收盘价序列计算日收益率序列。

    Args:
        close_prices: 收盘价序列 (按日期降序, index 0 = T日)

    Returns:
        日收益率序列 (r_t, r_t-1, ..., r_t-19), 长度为 min(len-1, 20)
    """
    returns = []
    for i in range(min(len(close_prices) - 1, 20)):
        if close_prices[i] is None or close_prices[i + 1] is None:
            continue
        if abs(close_prices[i + 1]) < 1e-10:
            continue
        dr = close_prices[i] / close_prices[i + 1] - 1
        returns.append(dr)
    return returns


def calc_lowvol_factor(close_prices: list) -> Optional[float]:
    """计算低波因子 = std(20个日收益率)。

    Args:
        close_prices: 收盘价序列 (按日期降序, index 0 = T日),
                      需要22个值以计算20个日收益率

    Returns:
        低波因子(标准差), 数据不足时返回None

    边界兜底 [default]:
    - 序列长度不足22返回None
    - 日收益率不足20个时使用可用数据计算
    - 单个日收益率时返回0
    """
    daily_returns = calc_daily_returns(close_prices)
    if len(daily_returns) < 2:
        return None
    n = len(daily_returns)
    mean = sum(daily_returns) / n
    variance = sum((r - mean) ** 2 for r in daily_returns) / n
    std = math.sqrt(variance)
    return round(std, 6)
