"""[default] ETF综合评分计算测试."""
from datetime import date

from src.morning_report.calc.ranking import calc_rank_scores
from src.morning_report.calc.scoring import calc_composite_scores, build_top5_result
from src.morning_report.models import CalcStatus, MarketTag


def test_composite_scoring():
    today = date.today()
    codes = ["A", "B", "C"]
    names = {"A": "ETF-A", "B": "ETF-B", "C": "ETF-C"}

    heat_items = [(c, 1.0, CalcStatus.SUCCESS) for c in codes]  # all same
    momentum_items = [("A", 2.0, CalcStatus.SUCCESS), ("B", 1.0, CalcStatus.SUCCESS), ("C", 3.0, CalcStatus.SUCCESS)]
    liquidity_items = [("A", 100.0, CalcStatus.SUCCESS), ("B", 200.0, CalcStatus.SUCCESS), ("C", 300.0, CalcStatus.SUCCESS)]
    low_vol_items = [("A", 0.1, CalcStatus.SUCCESS), ("B", 0.2, CalcStatus.SUCCESS), ("C", 0.3, CalcStatus.SUCCESS)]

    heat_ranks = calc_rank_scores(heat_items, True)
    momentum_ranks = calc_rank_scores(momentum_items, True)
    liquidity_ranks = calc_rank_scores(liquidity_items, True)
    low_vol_ranks = calc_rank_scores(low_vol_items, False)  # ASC

    scores = calc_composite_scores(
        heat_ranks, momentum_ranks, liquidity_ranks, low_vol_ranks,
        today, names, MarketTag.ACTIVE,
    )

    assert len(scores) == 3
    assert scores[0].rank == 1
    assert scores[0].composite_score >= scores[-1].composite_score


def test_build_top5():
    today = date.today()
    from src.morning_report.models import ETFScore
    scores = [
        ETFScore("A", "ETF-A", today, 0.5, 0.3, 0.08, 0.03, 0.44, 1, "sector1", ["tag1"], MarketTag.ACTIVE),
        ETFScore("B", "ETF-B", today, 0.4, 0.3, 0.08, 0.03, 0.42, 2, "sector2", ["tag2"], MarketTag.ACTIVE),
        ETFScore("C", "ETF-C", today, 0.3, 0.3, 0.08, 0.03, 0.40, 3, "sector1", ["tag3"], MarketTag.ACTIVE),
        ETFScore("D", "ETF-D", today, 0.2, 0.3, 0.08, 0.03, 0.38, 4, "sector3", ["tag4"], MarketTag.ACTIVE),
        ETFScore("E", "ETF-E", today, 0.1, 0.3, 0.08, 0.03, 0.36, 5, "sector4", ["tag5"], MarketTag.ACTIVE),
        ETFScore("F", "ETF-F", today, 0.0, 0.3, 0.08, 0.03, 0.34, 6, "sector5", ["tag6"], MarketTag.ACTIVE),
    ]
    result = build_top5_result(scores, today, MarketTag.ACTIVE, 6)
    assert len(result.top_etfs) == 5
    assert result.market_tag == "积极参与"
    assert result.total_etf_count == 6
    assert len(result.sectors) <= 5
