"""动量因子计算单元测试。"""

import unittest
from src.data.calculations.momentum_factor import (
    calc_momentum_factor,
    calc_20d_momentum_median,
)


class TestMomentumFactor(unittest.TestCase):
    def test_basic(self):
        prices = [2.1, 2.0, 1.9, 1.5, 1.2, 1.0, 0.9, 0.8]
        result = calc_momentum_factor(prices)
        self.assertAlmostEqual(result, 1.0)

    def test_decline(self):
        prices = [0.9, 1.0, 1.2, 1.5, 1.8, 2.0, 2.1, 2.2]
        result = calc_momentum_factor(prices)
        self.assertAlmostEqual(result, -0.5)

    def test_insufficient_data(self):
        prices = [1.0, 2.0, 3.0]
        result = calc_momentum_factor(prices)
        self.assertIsNone(result)

    def test_zero_divisor(self):
        prices = [1.0, 2.0, 3.0, 4.0, 5.0, 0.0, 1.0, 2.0]
        result = calc_momentum_factor(prices)
        self.assertIsNone(result)

    def test_flat_prices(self):
        prices = [1.0] * 10
        result = calc_momentum_factor(prices)
        self.assertAlmostEqual(result, 0.0)


class Test20dMomentumMedian(unittest.TestCase):
    def test_basic(self):
        prices = [p / 20.0 for p in range(21, 0, -1)]
        result = calc_20d_momentum_median(prices)
        self.assertIsNotNone(result)

    def test_insufficient_data(self):
        prices = [1.0] * 10
        result = calc_20d_momentum_median(prices)
        self.assertIsNone(result)

    def test_all_same(self):
        prices = [1.0] * 22
        result = calc_20d_momentum_median(prices)
        self.assertAlmostEqual(result, 0.0)

    def test_median_calculation(self):
        prices = [2.0, 1.0] + [1.0] * 19
        result = calc_20d_momentum_median(prices)
        self.assertAlmostEqual(result, 0.0)


if __name__ == "__main__":
    unittest.main()
