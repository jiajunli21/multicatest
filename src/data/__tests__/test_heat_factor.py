"""热度因子计算单元测试。"""

import math
import unittest
from src.data.calculations.heat_factor import (
    calc_search_heat,
    calc_first_buy_heat,
    calc_z_score,
    calc_heat_factor,
)


class TestSearchHeat(unittest.TestCase):
    def test_basic(self):
        result = calc_search_heat(100, 50)
        expected = math.log(1 + 100 + 3 * 50)
        self.assertEqual(result, expected)

    def test_zero(self):
        result = calc_search_heat(0, 0)
        self.assertEqual(result, 0.0)

    def test_large_values(self):
        result = calc_search_heat(10000, 5000)
        self.assertGreater(result, 0)


class TestFirstBuyHeat(unittest.TestCase):
    def test_basic(self):
        result = calc_first_buy_heat(200, 50, 20)
        expected = math.log(1 + 200 + 5 * 50 + 20 * 20)
        self.assertEqual(result, expected)

    def test_zero(self):
        result = calc_first_buy_heat(0, 0, 0)
        self.assertEqual(result, 0.0)


class TestZScore(unittest.TestCase):
    def test_standard_normal(self):
        result = calc_z_score(1.0, [0.0, 1.0, 2.0])
        self.assertLess(abs(result - 0.0), 0.01)

    def test_above_mean(self):
        result = calc_z_score(2.0, [0.0, 1.0, 2.0])
        self.assertGreater(result, 0)

    def test_zero_std_returns_zero(self):
        result = calc_z_score(5.0, [5.0, 5.0, 5.0])
        self.assertEqual(result, 0.0)

    def test_empty_window(self):
        result = calc_z_score(5.0, [])
        self.assertEqual(result, 0.0)

    def test_single_value(self):
        result = calc_z_score(5.0, [5.0])
        self.assertEqual(result, 0.0)


class TestHeatFactor(unittest.TestCase):
    def test_basic(self):
        sousuo = [100] * 20
        sousuo_click = [50] * 20
        fenshi = [200] * 20
        add = [30] * 20
        buy = [10] * 20
        result = calc_heat_factor(sousuo, sousuo_click, fenshi, add, buy)
        self.assertIsNotNone(result)
        self.assertEqual(result["search_heat_z"], 0.0)
        self.assertEqual(result["first_buy_heat_z"], 0.0)
        self.assertEqual(result["heat_factor"], 0.0)

    def test_with_variation(self):
        sousuo = [200, 180, 160, 140, 120] + [100] * 15
        sousuo_click = [100, 90, 80, 70, 60] + [50] * 15
        fenshi = [400, 360, 320, 280, 240] + [200] * 15
        add = [60, 50, 40, 30, 20] + [10] * 15
        buy = [30, 25, 20, 15, 10] + [5] * 15
        result = calc_heat_factor(sousuo, sousuo_click, fenshi, add, buy)
        self.assertIsNotNone(result)
        self.assertGreater(result["search_heat_z"], 0)
        self.assertGreater(result["first_buy_heat_z"], 0)
        self.assertGreater(result["heat_factor"], 0)

    def test_insufficient_data(self):
        result = calc_heat_factor([100], [50], [200], [30], [10])
        self.assertIsNone(result)

    def test_formula_weights(self):
        sousuo = [200, 100] + [100] * 18
        sousuo_click = [100, 50] + [50] * 18
        fenshi = [100] * 20
        add = [10] * 20
        buy = [5] * 20
        result = calc_heat_factor(sousuo, sousuo_click, fenshi, add, buy)
        expected = 0.55 * result["search_heat_z"] + 0.45 * result["first_buy_heat_z"]
        self.assertLess(abs(result["heat_factor"] - expected), 1e-6)


if __name__ == "__main__":
    unittest.main()
