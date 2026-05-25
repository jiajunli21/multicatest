"""[default] 流动性因子计算测试."""
from datetime import date, timedelta

from src.morning_report.calc.liquidity import calc_liquidity_factor
from src.morning_report.models import DailyPrice


def test_liquidity_basic():
    today = date.today()
    prices = [
        DailyPrice(date=today - timedelta(days=i), etf_code="510050",
                   close_price=2.0, turnover=500_000_000 + i * 1_000_000)
        for i in range(25)
    ]
    result = calc_liquidity_factor("510050", today, prices, window=20)
    assert result.status.value == "success"
    assert result.avg_turnover_20d > 0
    assert result.sample_count == 20


def test_liquidity_insufficient_sample():
    today = date.today()
    prices = [
        DailyPrice(date=today - timedelta(days=i), etf_code="510050",
                   close_price=2.0, turnover=500_000_000)
        for i in range(10)
    ]
    result = calc_liquidity_factor("510050", today, prices, window=20)
    assert result.status.value == "insufficient_sample"


def test_liquidity_not_calculable():
    result = calc_liquidity_factor("510050", date.today(), [], window=20)
    assert result.status.value == "not_calculable"
