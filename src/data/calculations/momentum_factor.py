"""动量因子计算。[default]

DI-007: 动量因子 = C_t-1 / C_t-5 - 1

基于收盘价(unitNav序列)计算。[verified: unitNav online]
排名方向: DESC (值越大排名越高)

时间口径: 暂按自然日模拟 [pending: 交易日口径]
"""

from typing import Optional


def calc_momentum_factor(close_prices: list) -> Optional[float]:
    """计算动量因子 = C_t-1 / C_t-5 - 1。

    Args:
        close_prices: 收盘价序列 (按日期降序, index 0 = T日)

    Returns:
        动量因子值, 数据不足时返回None

    边界兜底 [default]:
    - 序列长度不足6时返回None
    - C_t-5 为0或接近0时返回None
    """
    if len(close_prices) < 6:
        return None
    c_t_minus_1 = close_prices[1]
    c_t_minus_5 = close_prices[5]
    if c_t_minus_5 is None or abs(c_t_minus_5) < 1e-10:
        return None
    return round(c_t_minus_1 / c_t_minus_5 - 1, 6)


def calc_20d_momentum_median(close_prices_sequence: list) -> Optional[float]:
    """计算20日动量中位数 (用于标签判定)。

    每日动量 = C_t / C_t-1 - 1, 取最近20个日动量的中位数。

    Args:
        close_prices_sequence: 收盘价序列 (按日期降序, index 0 = T日),
                               需要至少21个值以计算20个日收益率

    Returns:
        20日动量中位数
    """
    if len(close_prices_sequence) < 21:
        return None
    daily_returns = []
    for i in range(20):
        if close_prices_sequence[i] is None or close_prices_sequence[i + 1] is None:
            continue
        if abs(close_prices_sequence[i + 1]) < 1e-10:
            continue
        dr = close_prices_sequence[i] / close_prices_sequence[i + 1] - 1
        daily_returns.append(dr)
    if not daily_returns:
        return None
    sorted_returns = sorted(daily_returns)
    n = len(sorted_returns)
    if n % 2 == 1:
        return round(sorted_returns[n // 2], 6)
    return round((sorted_returns[n // 2 - 1] + sorted_returns[n // 2]) / 2, 6)
