"""标签计算单元测试。"""

import unittest
from src.data.calculations.labels import calc_market_tag, get_mock_fund_tags


class TestMarketTag(unittest.TestCase):
    def test_cautious(self):
        self.assertEqual(calc_market_tag(-0.05), "谨慎参与")
        self.assertEqual(calc_market_tag(-0.031), "谨慎参与")

    def test_active(self):
        self.assertEqual(calc_market_tag(-0.03), "积极参与")
        self.assertEqual(calc_market_tag(0.0), "积极参与")
        self.assertEqual(calc_market_tag(0.05), "积极参与")

    def test_none_default(self):
        self.assertEqual(calc_market_tag(None), "积极参与")


class TestMockFundTags(unittest.TestCase):
    def test_configured_etf(self):
        config = {"510050": ["低估值", "分红稳定"], "512880": ["放量突破"]}
        tags = get_mock_fund_tags("510050", config)
        self.assertEqual(tags, ["低估值", "分红稳定"])

    def test_unconfigured_etf(self):
        config = {"510050": ["低估值"]}
        tags = get_mock_fund_tags("999999", config)
        self.assertEqual(tags, [])

    def test_empty_config(self):
        tags = get_mock_fund_tags("510050", {})
        self.assertEqual(tags, [])


if __name__ == "__main__":
    unittest.main()
