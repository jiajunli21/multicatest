"""热度因子计算。[mock]

DI-004: 搜索热度Z分数 = (T日值 - 20日窗口均值) / 20日窗口标准差
DI-005: 首购热度Z分数 = (T日值 - 20日窗口均值) / 20日窗口标准差
DI-006: 热度因子 = 0.55 * 搜索热度Z + 0.45 * 首购热度Z

热度原始字段(sousuo_uv, sousuo_click_uv, fenshi_uv, add_uv, buy_uv)为Mock数据。
[pending: 真实sousuo_uv等数据源]

T日搜索热度 = log(1 + sousuo_uv + 3 * sousuo_click_uv)
T日首购热度 = log(1 + fenshi_uv + 5 * add_uv + 20 * buy_uv)

排名方向: DESC (值越大排名越高)
"""

import math
from typing import Optional


def calc_search_heat(sousuo_uv: float, sousuo_click_uv: float) -> float:
    """计算T日搜索热度值。

    T日搜索热度 = log(1 + sousuo_uv + 3 * sousuo_click_uv)
    """
    return math.log(1 + sousuo_uv + 3 * sousuo_click_uv)


def calc_first_buy_heat(fenshi_uv: float, add_uv: float, buy_uv: float) -> float:
    """计算T日首购热度值。

    T日首购热度 = log(1 + fenshi_uv + 5 * add_uv + 20 * buy_uv)
    """
    return math.log(1 + fenshi_uv + 5 * add_uv + 20 * buy_uv)


def calc_z_score(value: float, window_values: list) -> float:
    """计算Z分数 = (value - mean) / std。

    边界兜底 [default]:
    - 窗口标准差为0时返回0
    - 窗口值不足时使用可用数据计算
    - 空窗口返回0
    """
    if not window_values:
        return 0.0
    n = len(window_values)
    mean = sum(window_values) / n
    variance = sum((v - mean) ** 2 for v in window_values) / n
    std = math.sqrt(variance)
    if std < 1e-10:
        return 0.0
    return (value - mean) / std


def calc_heat_factor(
    sousuo_uv_window: list,
    sousuo_click_uv_window: list,
    fenshi_uv_window: list,
    add_uv_window: list,
    buy_uv_window: list,
) -> Optional[dict]:
    """计算热度因子。

    Args:
        sousuo_uv_window: T日至T-19日搜索UV序列 (len=20, index 0 = T日)
        sousuo_click_uv_window: 搜索点击UV序列
        fenshi_uv_window: 分时UV序列
        add_uv_window: 加自选UV序列
        buy_uv_window: 购买UV序列

    Returns:
        dict with keys: search_heat_z, first_buy_heat_z, heat_factor
        数据不足时返回None
    """
    if len(sousuo_uv_window) < 2 or len(fenshi_uv_window) < 2:
        return None

    # 每日搜索热度
    search_heat_values = [
        calc_search_heat(sousuo_uv_window[i], sousuo_click_uv_window[i])
        for i in range(len(sousuo_uv_window))
    ]
    # 每日首购热度
    first_buy_heat_values = [
        calc_first_buy_heat(fenshi_uv_window[i], add_uv_window[i], buy_uv_window[i])
        for i in range(len(fenshi_uv_window))
    ]

    # T日值 = index 0
    t_search_heat = search_heat_values[0]
    t_first_buy_heat = first_buy_heat_values[0]

    # Z分数: 使用T日至T-19日窗口(全部20日)
    search_heat_z = calc_z_score(t_search_heat, search_heat_values)
    first_buy_heat_z = calc_z_score(t_first_buy_heat, first_buy_heat_values)

    # 热度因子
    heat_factor = 0.55 * search_heat_z + 0.45 * first_buy_heat_z

    return {
        "search_heat_z": round(search_heat_z, 6),
        "first_buy_heat_z": round(first_buy_heat_z, 6),
        "heat_factor": round(heat_factor, 6),
    }
