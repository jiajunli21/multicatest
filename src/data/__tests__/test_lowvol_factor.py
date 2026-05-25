"""低波因子计算单元测试。"""

import unittest
from src.data.calculations.lowvol_factor import calc_daily_returns, calc_lowvol_factor


class TestDailyReturns(unittest.TestCase):
    def test_basic(self):
        prices = [2.2, 2.0, 1.0]
        returns = calc_daily_returns(prices)
        self.assertEqual(len(returns), 2)
        self.assertAlmostEqual(returns[0], 0.1)
        self.assertAlmostEqual(returns[1], 1.0)

    def test_max_20(self):
        prices = list(range(30, 0, -1))
        returns = calc_daily_returns(prices)
        self.assertEqual(len(returns), 20)


class TestLowvolFactor(unittest.TestCase):
    def test_basic(self):
        prices = [1.0 + i * 0.01 for i in range(22)]
        prices.reverse()
        result = calc_lowvol_factor(prices)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)

    def test_constant_prices(self):
        prices = [2.0] * 22
        result = calc_lowvol_factor(prices)
        self.assertAlmostEqual(result, 0.0)

    def test_insufficient_data(self):
        prices = [1.0, 2.0]
        result = calc_lowvol_factor(prices)
        self.assertIsNone(result)

    def test_single_return(self):
        prices = [2.0, 1.0]
        result = calc_lowvol_factor(prices)
        self.assertIsNone(result)

    def test_volatile_prices(self):
        prices = [1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0] * 3
        result = calc_lowvol_factor(prices)
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.5)


if __name__ == "__main__":
    unittest.main()
