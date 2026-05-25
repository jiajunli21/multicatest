"""[default] 排名计算测试."""
from src.morning_report.calc.ranking import calc_rank_scores
from src.morning_report.models import CalcStatus


def test_ranking_desc():
    items = [
        ("A", 10.0, CalcStatus.SUCCESS),
        ("B", 5.0, CalcStatus.SUCCESS),
        ("C", 8.0, CalcStatus.SUCCESS),
    ]
    ranks = calc_rank_scores(items, descending=True)
    by_code = {r.etf_code: r for r in ranks}

    assert by_code["A"].rank == 1  # 最高分
    assert by_code["C"].rank == 2
    assert by_code["B"].rank == 3
    assert by_code["A"].rank_score == (3 - 1) / 3  # 2/3
    assert by_code["B"].rank_score == 0.0  # (3-3)/3=0


def test_ranking_asc():
    items = [
        ("A", 0.01, CalcStatus.SUCCESS),
        ("B", 0.05, CalcStatus.SUCCESS),
        ("C", 0.02, CalcStatus.SUCCESS),
    ]
    ranks = calc_rank_scores(items, descending=False)
    by_code = {r.etf_code: r for r in ranks}

    assert by_code["A"].rank == 1  # 最小
    assert by_code["C"].rank == 2
    assert by_code["B"].rank == 3


def test_ranking_tie():
    """并列同名次，后续顺延."""
    items = [
        ("A", 10.0, CalcStatus.SUCCESS),
        ("B", 10.0, CalcStatus.SUCCESS),
        ("C", 5.0, CalcStatus.SUCCESS),
    ]
    ranks = calc_rank_scores(items, descending=True)
    by_code = {r.etf_code: r for r in ranks}

    assert by_code["A"].rank == 1
    assert by_code["B"].rank == 1  # 并列
    assert by_code["C"].rank == 3  # 顺延


def test_ranking_not_calculable():
    items = [
        ("A", 10.0, CalcStatus.SUCCESS),
        ("B", 5.0, CalcStatus.NOT_CALCULABLE),
        ("C", 8.0, CalcStatus.SUCCESS),
    ]
    ranks = calc_rank_scores(items, descending=True)
    by_code = {r.etf_code: r for r in ranks}

    assert by_code["B"].rank == 3  # 排在最后
    assert by_code["B"].rank_score == 0.0


def test_ranking_empty():
    assert calc_rank_scores([], descending=True) == []
