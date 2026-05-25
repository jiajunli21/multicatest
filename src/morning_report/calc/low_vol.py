"""低波因子计算模块。

Status: [default] — 基于收盘价序列计算，收盘价来源 [verified] (unitNav).

公式:
- 日收益率_t = 收盘价_t / 收盘价_t-1 - 1
- 低波因子 = std(日收益率_t-20, ..., 日收益率_t-1)
- 排名 ASC（波动越低越好）
"""

import math
from datetime import date
from typing import Optional

from ..models import CalcStatus, DataSource, DailyPrice, LowVolFactorResult


def calc_daily_returns(prices: list[float]) -> list[float]:
    """从价格序列计算日收益率序列.

    Args:
        prices: 按时间升序排列的收盘价列表

    Returns:
        日收益率列表 (len = len(prices) - 1)
    """
    if len(prices) < 2:
        return []
    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] > 0:
            r = prices[i] / prices[i - 1] - 1.0
        else:
            r = 0.0
        returns.append(r)
    return returns


def calc_low_vol_factor(
    etf_code: str,
    calc_date: date,
    price_series: list[DailyPrice],
    window: int = 20,
) -> LowVolFactorResult:
    """计算低波因子 = std(最近 20 个日收益率).

    边界规则 [default]:
    - 标准差为 0 时保留 0.0（Z 分数阶段处理为 0）
    - 价格序列不足 → INSUFFICIENT_SAMPLE
    - 无可用数据 → NOT_CALCULABLE
    - 日收益率为 0 的交易日（停牌）不剔除，纳入计算

    Args:
        etf_code: ETF 代码
        calc_date: 计算日期
        price_series: 按日期升序排列的价格序列（需最近 window+1 个交易日）
        window: 日收益率窗口大小 (默认 20)
    """
    if not price_series or len(price_series) < 2:
        return LowVolFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            daily_returns=[],
            low_vol_factor=0.0,
            status=CalcStatus.NOT_CALCULABLE,
        )

    # 过滤 calc_date 及之前的有效价格
    prices = [
        p.close_price for p in price_series
        if p.date <= calc_date and p.close_price > 0
    ]

    daily_returns = calc_daily_returns(prices)

    if not daily_returns:
        return LowVolFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            daily_returns=[],
            low_vol_factor=0.0,
            status=CalcStatus.NOT_CALCULABLE,
        )

    # 取最近 window 个日收益率
    sample = daily_returns[-window:]

    if len(sample) < 2:
        return LowVolFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            daily_returns=[round(r, 6) for r in sample],
            low_vol_factor=0.0,
            status=CalcStatus.INSUFFICIENT_SAMPLE,
        )

    mean = sum(sample) / len(sample)
    variance = sum((r - mean) ** 2 for r in sample) / len(sample)
    std = math.sqrt(variance)

    status = CalcStatus.SUCCESS
    if len(sample) < window:
        status = CalcStatus.INSUFFICIENT_SAMPLE

    return LowVolFactorResult(
        etf_code=etf_code,
        calc_date=calc_date,
        daily_returns=[round(r, 6) for r in sample],
        low_vol_factor=round(std, 8),
        status=status,
        source=DataSource.DEFAULT,
    )
