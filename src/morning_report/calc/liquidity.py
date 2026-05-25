"""流动性因子计算模块。

Status: [default] — 基于成交额序列计算。
turnover 指标 deprecated → 从行情接口取原始数据自行计算 [default].

公式（默认假设）:
- 流动性因子 = 近 20 个可用交易日成交额均值
- 排名 DESC（成交额越高，流动性越好）
"""

from datetime import date
from typing import Optional

from ..models import CalcStatus, DataSource, DailyPrice, LiquidityFactorResult


def calc_liquidity_factor(
    etf_code: str,
    calc_date: date,
    price_series: list[DailyPrice],
    window: int = 20,
) -> LiquidityFactorResult:
    """计算流动性因子 = 近 N 个可用交易日成交额均值 [default].

    边界规则 [default]:
    - 样本不足时按已有样本计算，标记 insufficient_sample
    - 无可用成交额数据 → NOT_CALCULABLE

    Args:
        etf_code: ETF 代码
        calc_date: 计算日期
        price_series: 含成交额字段的行情序列（按日期升序）
        window: 窗口大小 (默认 20)
    """
    # 过滤有成交额数据的交易日
    turnover_values = [
        p.turnover for p in price_series
        if p.turnover > 0 and p.date <= calc_date
    ]

    if not turnover_values:
        return LiquidityFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            avg_turnover_20d=0.0,
            status=CalcStatus.NOT_CALCULABLE,
            sample_count=0,
        )

    # 取最近 N 个可用交易日的成交额
    sample = turnover_values[-window:]
    avg_turnover = sum(sample) / len(sample)

    status = CalcStatus.SUCCESS
    if len(sample) < window:
        status = CalcStatus.INSUFFICIENT_SAMPLE

    return LiquidityFactorResult(
        etf_code=etf_code,
        calc_date=calc_date,
        avg_turnover_20d=round(avg_turnover, 2),
        status=status,
        sample_count=len(sample),
        source=DataSource.DEFAULT,
    )
