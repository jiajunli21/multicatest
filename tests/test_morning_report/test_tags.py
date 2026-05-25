"""[default] 标签计算测试."""
from datetime import date, timedelta

from src.morning_report.calc.tags import calc_market_tag, get_etf_tags
from src.morning_report.models import DailyPrice, MarketTag


def _make_price_series(etf_code: str, start_price: float, daily_change: float) -> list[DailyPrice]:
    """生成覆盖 today-25 到 today 的价格序列."""
    today = date.today()
    result = []
    for i in range(26):
        days_ago = 25 - i
        d = today - timedelta(days=days_ago)
        price = start_price + daily_change * i
        result.append(DailyPrice(date=d, etf_code=etf_code, close_price=price))
    result.sort(key=lambda p: p.date)
    return result


def test_market_tag_bullish():
    """3个ETF 20日动量中位数 > -0.03 → 积极参与."""
    today = date.today()
    series_list = [
        ("A", _make_price_series("A", 1.85, 0.006)),  # rising
        ("B", _make_price_series("B", 2.85, 0.006)),
        ("C", _make_price_series("C", 0.85, 0.006)),
    ]
    tag = calc_market_tag(series_list, today)
    assert tag == MarketTag.ACTIVE


def test_market_tag_bearish():
    """3个ETF 20日动量中位数 < -0.03 → 谨慎参与."""
    today = date.today()
    series_list = [
        ("A", _make_price_series("A", 2.15, -0.006)),  # declining
        ("B", _make_price_series("B", 3.15, -0.006)),
        ("C", _make_price_series("C", 1.15, -0.006)),
    ]
    tag = calc_market_tag(series_list, today)
    assert tag == MarketTag.CAUTIOUS


def test_market_tag_insufficient():
    """不足3个ETF时默认积极参与."""
    today = date.today()
    tag = calc_market_tag([], today)
    assert tag == MarketTag.ACTIVE

    # 单个 ETF 也不足
    single = _make_price_series("X", 2.0, -0.01)
    tag2 = calc_market_tag([("X", single)], today)
    assert tag2 == MarketTag.ACTIVE


def test_get_etf_tags():
    tags = get_etf_tags("510050")
    assert isinstance(tags, list)
    assert len(tags) > 0


def test_get_etf_tags_unknown():
    tags = get_etf_tags("UNKNOWN")
    assert isinstance(tags, list)
