"""[default] 热度因子计算测试."""
import math
from datetime import date

from src.morning_report.calc.heat import (
    calc_search_heat,
    calc_buy_heat,
    calc_z_score,
    calc_heat_factor_for_etf,
)
from src.morning_report.models import HeatRawFields


def test_calc_search_heat():
    assert calc_search_heat(1000, 200) == math.log1p(1000 + 3 * 200)
    assert calc_search_heat(0, 0) == 0.0


def test_calc_buy_heat():
    assert calc_buy_heat(500, 50, 10) == math.log1p(500 + 5 * 50 + 20 * 10)
    assert calc_buy_heat(0, 0, 0) == 0.0


def test_z_score_normal():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    z = calc_z_score(5.0, values)
    # mean=3.0, std=sqrt(2)≈1.414
    expected = (5.0 - 3.0) / math.sqrt(2.0)
    assert abs(z - expected) < 1e-10


def test_z_score_zero_std():
    """标准差为0时Z分数记为0 [default]."""
    z = calc_z_score(5.0, [5.0, 5.0, 5.0])
    assert z == 0.0


def test_z_score_empty():
    assert calc_z_score(1.0, []) == 0.0


def test_z_score_single_value():
    assert calc_z_score(1.0, [1.0]) == 0.0


def test_heat_factor_success():
    """基本热度因子计算."""
    today = date.today()
    fields = [HeatRawFields(
        date=today,
        etf_code="510050",
        sousuo_uv=5000 + i * 100,
        sousuo_click_uv=800,
        fenshi_uv=3000,
        add_uv=200,
        buy_uv=50,
    ) for i in range(20)]

    result = calc_heat_factor_for_etf("510050", today, fields)
    assert result.search_heat_t > 0
    assert result.buy_heat_t > 0
    assert result.heat_factor != 0.0


def test_heat_factor_not_calculable():
    result = calc_heat_factor_for_etf("510050", date.today(), [])
    assert result.status.value == "not_calculable"
