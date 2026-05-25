"""[default] 低波因子计算测试."""
import math
from datetime import date, timedelta

from src.morning_report.calc.low_vol import calc_daily_returns, calc_low_vol_factor
from src.morning_report.models import DailyPrice


def test_daily_returns():
    prices = [2.0, 2.2, 2.0, 1.8, 2.0]
    returns = calc_daily_returns(prices)
    assert len(returns) == 4
    assert abs(returns[0] - 0.1) < 1e-10  # 2.2/2.0 - 1
    assert abs(returns[1] - (2.0 / 2.2 - 1)) < 1e-10
    assert abs(returns[2] - (1.8 / 2.0 - 1)) < 1e-10


def test_daily_returns_empty():
    assert calc_daily_returns([]) == []
    assert calc_daily_returns([1.0]) == []


def test_low_vol_basic():
    today = date.today()
    prices = [
        DailyPrice(date=today - timedelta(days=i), etf_code="510050",
                   close_price=2.0 + 0.01 * i)
        for i in range(25)
    ]
    result = calc_low_vol_factor("510050", today, prices)
    assert result.status.value == "success"
    assert result.low_vol_factor >= 0


def test_low_vol_zero_std():
    """所有日收益率相同时标准差为0 [default]."""
    today = date.today()
    prices = [
        DailyPrice(date=today - timedelta(days=i), etf_code="510050",
                   close_price=2.0)
        for i in range(25)
    ]
    result = calc_low_vol_factor("510050", today, prices)
    assert result.low_vol_factor == 0.0


def test_low_vol_not_calculable():
    result = calc_low_vol_factor("510050", date.today(), [])
    assert result.status.value == "not_calculable"


def test_low_vol_insufficient_sample():
    today = date.today()
    prices = [
        DailyPrice(date=today - timedelta(days=i), etf_code="510050",
                   close_price=2.0 + 0.01 * i)
        for i in range(4)
    ]
    result = calc_low_vol_factor("510050", today, prices)
    assert result.status.value in ("insufficient_sample", "not_calculable")
