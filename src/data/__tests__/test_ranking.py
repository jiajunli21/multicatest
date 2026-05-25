"""排名与综合评分计算单元测试。"""

import unittest
from src.data.calculations.ranking import (
    rank_values,
    calc_rank_score,
    calc_composite_score,
    compute_all_rankings,
    get_top_n,
)


class TestRankValues(unittest.TestCase):
    def test_desc(self):
        values = [("A", 10.0), ("B", 5.0), ("C", 8.0)]
        result = rank_values(values, "DESC")
        ranks = {code: rank for code, _, rank in result}
        self.assertEqual(ranks["A"], 1)
        self.assertEqual(ranks["C"], 2)
        self.assertEqual(ranks["B"], 3)

    def test_asc(self):
        values = [("A", 10.0), ("B", 5.0), ("C", 8.0)]
        result = rank_values(values, "ASC")
        ranks = {code: rank for code, _, rank in result}
        self.assertEqual(ranks["B"], 1)
        self.assertEqual(ranks["C"], 2)
        self.assertEqual(ranks["A"], 3)

    def test_ties(self):
        values = [("A", 10.0), ("B", 10.0), ("C", 5.0)]
        result = rank_values(values, "DESC")
        ranks = {code: rank for code, _, rank in result}
        self.assertEqual(ranks["A"], 1)
        self.assertEqual(ranks["B"], 1)
        self.assertEqual(ranks["C"], 3)

    def test_none_values_last(self):
        values = [("A", 10.0), ("B", None), ("C", 5.0)]
        result = rank_values(values, "DESC")
        ranks = {code: rank for code, _, rank in result}
        self.assertEqual(ranks["A"], 1)
        self.assertEqual(ranks["C"], 2)
        self.assertEqual(ranks["B"], 3)


class TestRankScore(unittest.TestCase):
    def test_first(self):
        self.assertAlmostEqual(calc_rank_score(1, 100), 1.0)

    def test_last(self):
        self.assertAlmostEqual(calc_rank_score(100, 100), 0.01)

    def test_middle(self):
        self.assertAlmostEqual(calc_rank_score(50, 100), 0.51)


class TestCompositeScore(unittest.TestCase):
    def test_basic(self):
        score = calc_composite_score(0.8, 0.6, 0.4, 0.2)
        expected = 0.50 * 0.8 + 0.35 * 0.6 + 0.10 * 0.4 + 0.05 * 0.2
        self.assertAlmostEqual(score, expected)

    def test_max_score(self):
        score = calc_composite_score(1.0, 1.0, 1.0, 1.0)
        self.assertAlmostEqual(score, 1.0)

    def test_min_score(self):
        score = calc_composite_score(0.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(score, 0.0)


class TestComputeAllRankings(unittest.TestCase):
    def test_basic(self):
        heat = {"A": 1.0, "B": 0.5, "C": 0.2}
        momentum = {"A": 0.1, "B": 0.3, "C": 0.2}
        liquidity = {"A": 100, "B": 200, "C": 150}
        lowvol = {"A": 0.02, "B": 0.01, "C": 0.03}

        results = compute_all_rankings(heat, momentum, liquidity, lowvol)
        self.assertEqual(len(results), 3)
        for code in ["A", "B", "C"]:
            self.assertIn("composite_score", results[code])
            self.assertIn("overall_rank", results[code])

    def test_rank_directions(self):
        heat = {"A": 0.9, "B": 0.5, "C": 0.1}
        momentum = {"A": 0.1, "B": 0.5, "C": 0.9}
        liquidity = {"A": 300, "B": 200, "C": 100}
        lowvol = {"A": 0.03, "B": 0.02, "C": 0.01}

        results = compute_all_rankings(heat, momentum, liquidity, lowvol)
        self.assertEqual(results["A"]["heat_rank"], 1)
        self.assertEqual(results["C"]["heat_rank"], 3)
        self.assertEqual(results["C"]["momentum_rank"], 1)
        self.assertEqual(results["A"]["liquidity_rank"], 1)
        self.assertEqual(results["A"]["lowvol_rank"], 3)
        self.assertEqual(results["C"]["lowvol_rank"], 1)


class TestGetTopN(unittest.TestCase):
    def test_basic(self):
        heat = {"A": 1.0, "B": 0.5, "C": 0.2, "D": 0.8, "E": 0.3}
        momentum = {k: 0.5 for k in heat}
        liquidity = {k: 100 for k in heat}
        lowvol = {k: 0.02 for k in heat}

        results = compute_all_rankings(heat, momentum, liquidity, lowvol)
        top3 = get_top_n(results, 3)
        self.assertEqual(len(top3), 3)


if __name__ == "__main__":
    unittest.main()
