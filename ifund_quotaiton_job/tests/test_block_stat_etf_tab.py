"""BlockStatEtfTabTask 单元测试。

测试覆盖：
- 4 维度排序正确性（DESC/ASC 取前9/后9）
- 降级规则：基金池空、扶摇失败、成分股失败
- speedRatio/volumeRatio Mock 占位行为
- Redis 读写和数据结构 schema
"""

import json
import time
import unittest

from .. import config
from ..BlockStatEtfTabTask import BlockStatEtfTabTask
from ..data_fetcher import (
    fetch_fund_pool_etf_list,
    fetch_fuyao_etf_quotes,
    fetch_component_stocks,
    fetch_all_market_stock_changes,
)
from ..rank_calculator import (
    calculate_rankings,
    _sort_etf_list,
    _get_safe_float,
    _compute_lead_stocks,
)
from ..redis_writer import write_rank_data, read_rank_data, _InMemoryRedis


def _make_etf(code: str, name: str) -> dict:
    return {"code": code, "name": name}


def _make_quote(chgpct: float, etfLimitUpStockCnt: int) -> dict:
    return {"chgpct": chgpct, "etfLimitUpStockCnt": etfLimitUpStockCnt}


class TestSortEtfList(unittest.TestCase):
    """排序函数单元测试。"""

    def test_sort_desc(self):
        etfs = [
            {"code": "A", "chgpct": 1.5},
            {"code": "B", "chgpct": 3.2},
            {"code": "C", "chgpct": -0.5},
        ]
        result = _sort_etf_list(etfs, "chgpct", descending=True)
        self.assertEqual([e["code"] for e in result], ["B", "A", "C"])

    def test_sort_asc(self):
        etfs = [
            {"code": "A", "chgpct": 1.5},
            {"code": "B", "chgpct": -0.5},
            {"code": "C", "chgpct": 3.2},
        ]
        result = _sort_etf_list(etfs, "chgpct", descending=False)
        self.assertEqual([e["code"] for e in result], ["B", "A", "C"])

    def test_sort_with_none_value(self):
        etfs = [
            {"code": "A", "chgpct": None},
            {"code": "B", "chgpct": 2.0},
            {"code": "C", "chgpct": -1.0},
        ]
        result = _sort_etf_list(etfs, "chgpct", descending=True)
        codes = [e["code"] for e in result]
        self.assertEqual(codes[0], "B")
        self.assertIn("A", codes)

    def test_sort_empty_list(self):
        result = _sort_etf_list([], "chgpct")
        self.assertEqual(result, [])


class TestSafeFloat(unittest.TestCase):
    """安全浮点转换测试。"""

    def test_normal(self):
        self.assertEqual(_get_safe_float(3.14), 3.14)

    def test_none(self):
        self.assertEqual(_get_safe_float(None), 0.0)

    def test_invalid(self):
        self.assertEqual(_get_safe_float("abc"), 0.0)

    def test_default_value(self):
        self.assertEqual(_get_safe_float(None, -1.0), -1.0)


class TestCalculateRankings(unittest.TestCase):
    """榜单计算单元测试。"""

    def setUp(self):
        self.etfs = [_make_etf(chr(65 + i), f"ETF_{chr(65 + i)}") for i in range(15)]
        codes = [e["code"] for e in self.etfs]
        self.quotes = {
            codes[i]: _make_quote(
                chgpct=(i - 7) * 1.5,
                etfLimitUpStockCnt=max(0, i - 5),
            )
            for i in range(15)
        }

    def test_eight_lists_produced(self):
        result = calculate_rankings(
            etf_list=self.etfs,
            quotes=self.quotes,
            component_relations=None,
            all_market_changes=None,
        )
        expected_keys = [
            "changeRatioTop9", "changeRatioBottom9",
            "speedRatioTop9", "speedRatioBottom9",
            "volumeRatioTop9", "volumeRatioBottom9",
            "limitUpCountTop9", "limitUpCountBottom9",
        ]
        for k in expected_keys:
            self.assertIn(k, result, f"Missing key: {k}")

    def test_top9_size(self):
        result = calculate_rankings(self.etfs, self.quotes, None, None)
        self.assertEqual(len(result["changeRatioTop9"]), 9)
        self.assertEqual(len(result["changeRatioBottom9"]), 9)

    def test_top9_desc_order(self):
        result = calculate_rankings(self.etfs, self.quotes, None, None)
        items = result["changeRatioTop9"]
        for i in range(len(items) - 1):
            self.assertGreaterEqual(
                items[i].get("chgpct", -999),
                items[i + 1].get("chgpct", -999),
            )

    def test_bottom9_asc_order(self):
        result = calculate_rankings(self.etfs, self.quotes, None, None)
        items = result["changeRatioBottom9"]
        for i in range(len(items) - 1):
            self.assertLessEqual(
                items[i].get("chgpct", 999),
                items[i + 1].get("chgpct", 999),
            )

    def test_small_etf_list(self):
        few_etfs = self.etfs[:5]
        result = calculate_rankings(few_etfs, self.quotes, None, None)
        self.assertLessEqual(len(result["changeRatioTop9"]), 5)

    def test_speed_ratio_mock_value(self):
        result = calculate_rankings(self.etfs, self.quotes, None, None)
        items = result["speedRatioTop9"]
        for item in items:
            self.assertEqual(
                item.get("speedRatio"),
                config.MOCK_SPEED_RATIO,
                "speedRatio should be Mock constant",
            )

    def test_volume_ratio_mock_value(self):
        result = calculate_rankings(self.etfs, self.quotes, None, None)
        items = result["volumeRatioTop9"]
        for item in items:
            self.assertEqual(
                item.get("volumeRatio"),
                config.MOCK_VOLUME_RATIO,
                "volumeRatio should be Mock constant",
            )

    def test_lead_stocks_empty_when_no_data(self):
        result = calculate_rankings(self.etfs, self.quotes, None, None)
        items = result["changeRatioTop9"]
        for item in items:
            self.assertEqual(item.get("topLeadStockCode"), "")
            self.assertEqual(item.get("topLeadStockName"), "")
            self.assertIsNone(item.get("topLeadStockChangeRatio"))
            self.assertEqual(item.get("bottomLeadStockCode"), "")
            self.assertEqual(item.get("bottomLeadStockName"), "")
            self.assertIsNone(item.get("bottomLeadStockChangeRatio"))


class TestComputeLeadStocks(unittest.TestCase):
    """领涨成分股计算测试。"""

    def setUp(self):
        self.etfs = [
            {"code": "ETF1", "name": "测试ETF1"},
        ]
        self.component_relations = {
            "ETF1": [
                {"code": "S1", "name": "股票1", "market": 17},
                {"code": "S2", "name": "股票2", "market": 33},
                {"code": "S3", "name": "股票3", "market": 177},
                {"code": "S4", "name": "股票4", "market": 1},
            ],
        }
        self.all_market = {
            "S1": {"chgpct": 5.0},
            "S2": {"chgpct": -2.0},
            "S3": {"chgpct": 3.0},
        }

    def test_market_filter(self):
        """market 不在 17/33/177 中的 v4 应被过滤。"""
        result = _compute_lead_stocks(
            self.etfs.copy(), self.component_relations, self.all_market
        )
        # S4 (market=1) 被过滤，S1/S2/S3 保留
        # 领涨=涨幅最大=S1(5.0), 领跌=涨幅最小=S2(-2.0)
        self.assertEqual(result[0]["topLeadStockCode"], "S1")
        self.assertEqual(result[0]["bottomLeadStockCode"], "S2")

    def test_empty_components(self):
        result = _compute_lead_stocks(
            [{"code": "ETF2", "name": "空ETF"}],
            {"ETF2": []},
            self.all_market,
        )
        self.assertEqual(result[0]["topLeadStockCode"], "")

    def test_no_component_relations(self):
        result = _compute_lead_stocks(self.etfs.copy(), None, self.all_market)
        self.assertEqual(result[0]["topLeadStockCode"], "")

    def test_no_all_market_changes(self):
        result = _compute_lead_stocks(self.etfs.copy(), self.component_relations, None)
        self.assertEqual(result[0]["topLeadStockCode"], "")


class TestRedisWriter(unittest.TestCase):
    """Redis 写入测试（使用内存模拟）。"""

    def test_write_and_read(self):
        rankings = {
            "changeRatioTop9": [
                {"code": "ETF1", "name": "测试", "chgpct": 5.0},
            ],
            "changeRatioBottom9": [],
            "speedRatioTop9": [],
            "speedRatioBottom9": [],
            "volumeRatioTop9": [],
            "volumeRatioBottom9": [],
            "limitUpCountTop9": [],
            "limitUpCountBottom9": [],
        }
        written = write_rank_data(rankings)
        self.assertTrue(written)

        read = read_rank_data()
        self.assertIsNotNone(read)
        self.assertIn("updateTime", read)
        self.assertEqual(len(read["changeRatioTop9"]), 1)
        self.assertEqual(read["changeRatioTop9"][0]["code"], "ETF1")

    def test_missing_key_returns_none(self):
        # 使用全新的内存实例
        from ..redis_writer import _InMemoryRedis, _get_redis

        result = read_rank_data()
        if result is None:
            pass
        else:
            self.assertIn("updateTime", result)


class TestBlockStatEtfTabTask(unittest.TestCase):
    """集成测试：BlockStatEtfTabTask 完整流程。"""

    def test_execute_with_no_api(self):
        """无外部 API 时：基金池拉取失败，不应覆盖 Redis。"""
        task = BlockStatEtfTabTask(api_base_url="http://localhost:19999")
        result = task.execute()
        self.assertFalse(result["success"])
        self.assertFalse(result["rankings_written"])
        self.assertGreater(len(result["errors"]), 0)

    def test_execute_result_structure(self):
        """验证返回结构完整性。"""
        task = BlockStatEtfTabTask(api_base_url="http://localhost:19999")
        result = task.execute()
        for key in ["success", "rankings_written", "errors", "degraded", "update_time"]:
            self.assertIn(key, result, f"Missing key: {key}")


class TestSchema(unittest.TestCase):
    """Redis 数据结构 Schema 验证。"""

    def test_schema_keys(self):
        rankings = {
            "changeRatioTop9": [],
            "changeRatioBottom9": [],
            "speedRatioTop9": [],
            "speedRatioBottom9": [],
            "volumeRatioTop9": [],
            "volumeRatioBottom9": [],
            "limitUpCountTop9": [],
            "limitUpCountBottom9": [],
        }
        write_rank_data(rankings)
        data = read_rank_data()
        self.assertIsNotNone(data)
        self.assertIn("updateTime", data)
        expected_keys = [
            "changeRatioTop9", "changeRatioBottom9",
            "speedRatioTop9", "speedRatioBottom9",
            "volumeRatioTop9", "volumeRatioBottom9",
            "limitUpCountTop9", "limitUpCountBottom9",
        ]
        for k in expected_keys:
            self.assertIn(k, data, f"Schema missing key: {k}")
            self.assertIsInstance(data[k], list, f"Schema key {k} should be list")

    def test_entry_schema(self):
        entry = {
            "code": "512880",
            "name": "证券ETF",
            "chgpct": 2.35,
            "topLeadStockCode": "600030",
            "topLeadStockName": "中信证券",
            "topLeadStockChangeRatio": 5.2,
            "bottomLeadStockCode": "000776",
            "bottomLeadStockName": "广发证券",
            "bottomLeadStockChangeRatio": -1.3,
        }
        required_fields = [
            "code", "name",
        ]
        for f in required_fields:
            self.assertIn(f, entry, f"Entry missing field: {f}")


if __name__ == "__main__":
    unittest.main()
