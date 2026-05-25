"""流动性因子计算。[default]

DI-008: 流动性因子 = 近20个可用交易日成交额均值

默认假设: 流动性因子 = 近20日成交额均值（PM接受）
[pending: 最终交易日口径]

成交额数据来源: 复用行情接口取原始成交额，Mock生成序列。
[danger]: fund-indic-search-test 中 turnover 指标为 deprecated。

排名方向: DESC (值越大排名越高)
"""

from typing import Optional


def calc_liquidity_factor(turnover_sequence: list) -> Optional[float]:
    """计算流动性因子 = 近20日成交额均值。

    Args:
        turnover_sequence: 成交额序列 (按日期降序, index 0 = T日), 需要至少1个值

    Returns:
        20日均成交额, 数据不足时返回可用数据的均值

    边界兜底 [default]:
    - 空序列返回None
    - 不足20日使用可用数据计算均值
    - 负值过滤为None，不参与计算
    """
    valid_values = [v for v in turnover_sequence if v is not None and v >= 0]
    if not valid_values:
        return None
    window = valid_values[:20]
    return round(sum(window) / len(window), 2)
