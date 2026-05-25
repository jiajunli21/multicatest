"""流动性因子计算单元测试。"""

import unittest
from src.data.calculations.liquidity_factor import calc_liquidity_factor


class TestLiquidityFactor(unittest.TestCase):
    def test_basic(self):
        turnovers = [1e9] * 20
        result = calc_liquidity_factor(turnovers)
        self.assertAlmostEqual(result, 1e9)

    def test_varied_values(self):
        turnovers = [1.0, 2.0, 3.0, 4.0, 5.0] * 4
        result = calc_liquidity_factor(turnovers)
        self.assertAlmostEqual(result, 3.0)

    def test_less_than_20(self):
        turnovers = [1e8, 2e8, 3e8]
        result = calc_liquidity_factor(turnovers)
        self.assertAlmostEqual(result, 2e8)

    def test_empty(self):
        result = calc_liquidity_factor([])
        self.assertIsNone(result)

    def test_with_none_values(self):
        turnovers = [1e9, None, 2e9, None, 3e9]
        result = calc_liquidity_factor(turnovers)
        self.assertAlmostEqual(result, 2e9)

    def test_with_negative_values_filtered(self):
        turnovers = [1e9, -1e8, 2e9]
        result = calc_liquidity_factor(turnovers)
        self.assertAlmostEqual(result, 1.5e9)

    def test_more_than_20(self):
        turnovers = [1.0] * 20 + [100.0] * 10
        result = calc_liquidity_factor(turnovers)
        self.assertAlmostEqual(result, 1.0)


if __name__ == "__main__":
    unittest.main()
