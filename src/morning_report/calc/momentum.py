"""动量因子计算模块。

Status: [default] — 基于收盘价序列计算，收盘价来源 [verified] (unitNav).

公式：
- 动量因子 = C_t-1 / C_t-5 - 1
- 排名 DESC（动量越大越好）
"""

from datetime import date, timedelta
from typing import Optional

from ..models import CalcStatus, DataSource, DailyPrice, MomentumFactorResult


def calc_momentum_factor(
    etf_code: str,
    calc_date: date,
    price_series: list[DailyPrice],
) -> MomentumFactorResult:
    """计算动量因子 = C_t-1 / C_t-5 - 1.

    边界规则 [default]:
    - 停牌或无行情数据 → NOT_CALCULABLE
    - 价格序列不足 → NOT_CALCULABLE
    - C_t-5 = 0 → NOT_CALCULABLE

    Args:
        etf_code: ETF 代码
        calc_date: 计算日期 (T 日)
        price_series: 按日期升序排列的收盘价序列，需包含 T-5 到 T-1
    """
    if not price_series:
        return MomentumFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            c_t_minus_1=0.0,
            c_t_minus_5=0.0,
            momentum_factor=0.0,
            status=CalcStatus.NOT_CALCULABLE,
        )

    # 按日期索引构建查找
    price_map = {p.date: p.close_price for p in price_series}

    t_minus_1 = calc_date - timedelta(days=1)
    t_minus_5 = calc_date - timedelta(days=5)

    # 查找最近可用交易日
    c_t_minus_1 = _find_nearest_price(t_minus_1, price_map, lookback=3)
    c_t_minus_5 = _find_nearest_price(t_minus_5, price_map, lookback=3)

    if c_t_minus_1 is None or c_t_minus_5 is None or c_t_minus_5 == 0.0:
        return MomentumFactorResult(
            etf_code=etf_code,
            calc_date=calc_date,
            c_t_minus_1=c_t_minus_1 or 0.0,
            c_t_minus_5=c_t_minus_5 or 0.0,
            momentum_factor=0.0,
            status=CalcStatus.NOT_CALCULABLE,
        )

    momentum = c_t_minus_1 / c_t_minus_5 - 1.0

    return MomentumFactorResult(
        etf_code=etf_code,
        calc_date=calc_date,
        c_t_minus_1=round(c_t_minus_1, 4),
        c_t_minus_5=round(c_t_minus_5, 4),
        momentum_factor=round(momentum, 6),
        status=CalcStatus.SUCCESS,
        source=DataSource.DEFAULT,
    )


def _find_nearest_price(
    target_date: date,
    price_map: dict[date, float],
    lookback: int = 3,
) -> Optional[float]:
    """查找最近可用交易日的收盘价（向前回溯最多 lookback 天）."""
    for i in range(lookback + 1):
        d = target_date - timedelta(days=i)
        if d in price_map and price_map[d] > 0:
            return price_map[d]
    return None
