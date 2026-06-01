import json
import time
import pytest
from unittest import mock

from fastapi.testclient import TestClient

from ifund_hq_project.app import app
from ifund_hq_project.models import RankData, EtfRankItem, ApiResponse

client = TestClient(app)

SAMPLE_RANK_JSON = json.dumps({
    "updateTime": 1717200000,
    "changeRatioTop9": [
        {
            "code": "512880", "name": "证券ETF", "chgpct": 2.35,
            "speedRatio": 0.0, "volumeRatio": 1.0, "etfLimitUpStockCnt": 3,
            "topLeadStockCode": "600030", "topLeadStockName": "中信证券",
            "topLeadStockChangeRatio": 5.2,
            "bottomLeadStockCode": "000776", "bottomLeadStockName": "广发证券",
            "bottomLeadStockChangeRatio": -1.3
        }
    ],
    "changeRatioBottom9": [],
    "speedRatioTop9": [],
    "speedRatioBottom9": [],
    "volumeRatioTop9": [],
    "volumeRatioBottom9": [],
    "limitUpCountTop9": [],
    "limitUpCountBottom9": []
})


def _clear_cache():
    from ifund_hq_project.cache import invalidate_local
    invalidate_local()


class TestResponseEnvelope:
    def test_envelope_structure(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=None):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        assert resp.status_code == 200
        body = resp.json()
        assert "code" in body
        assert "message" in body
        assert "data" in body
        assert "timestamp" in body
        assert isinstance(body["code"], int)
        assert isinstance(body["message"], str)
        assert isinstance(body["timestamp"], int)

    def test_no_bare_object(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=None):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        body = resp.json()
        # response must be envelope, not a bare rank object
        assert "code" in body
        assert "changeRatioTop9" not in body


class TestCacheHit:
    def test_caffeine_cache_hit(self):
        _clear_cache()
        from ifund_hq_project.cache import put_to_local
        put_to_local(SAMPLE_RANK_JSON)

        with mock.patch("ifund_hq_project.router.redis_get_rank_data") as mock_redis:
            resp = client.get("/api/v1/etf/plate-stat/rank")

        mock_redis.assert_not_called()
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]["changeRatioTop9"]) == 1
        assert body["data"]["changeRatioTop9"][0]["code"] == "512880"

    def test_caffeine_cache_miss_redis_hit(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=SAMPLE_RANK_JSON):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]["changeRatioTop9"]) == 1

        # second call should hit Caffeine
        with mock.patch("ifund_hq_project.router.redis_get_rank_data") as mock_redis:
            resp2 = client.get("/api/v1/etf/plate-stat/rank")
        mock_redis.assert_not_called()
        assert resp2.json()["code"] == 0


class TestRedisUnavailable:
    def test_redis_none_returns_empty(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=None):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["message"] == "success"
        data = body["data"]
        assert data["changeRatioTop9"] == []
        assert data["changeRatioBottom9"] == []
        assert data["speedRatioTop9"] == []
        assert data["speedRatioBottom9"] == []
        assert data["volumeRatioTop9"] == []
        assert data["volumeRatioBottom9"] == []
        assert data["limitUpCountTop9"] == []
        assert data["limitUpCountBottom9"] == []


class TestCorruptData:
    def test_corrupt_cache_falls_through_to_redis(self):
        _clear_cache()
        from ifund_hq_project.cache import put_to_local
        put_to_local("not valid json {{{")

        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=SAMPLE_RANK_JSON):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]["changeRatioTop9"]) == 1

    def test_corrupt_redis_returns_empty(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value="not json"):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["changeRatioTop9"] == []


class TestBusinessFieldPurity:
    def test_no_status_labels_in_response(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=SAMPLE_RANK_JSON):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        body_str = json.dumps(resp.json(), ensure_ascii=False)
        assert "[verified]" not in body_str
        assert "[mock]" not in body_str
        assert "[default]" not in body_str
        assert "[pending]" not in body_str

    def test_data_fields_are_pure_values(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=SAMPLE_RANK_JSON):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        item = resp.json()["data"]["changeRatioTop9"][0]
        assert item["code"] == "512880"
        assert item["name"] == "证券ETF"
        assert not item["code"].startswith("[")
        assert not item["name"].startswith("[")


class TestMockPassthrough:
    def test_speed_ratio_volume_ratio_mock_passthrough(self):
        _clear_cache()
        data_with_mock = json.dumps({
            "updateTime": 1717200000,
            "changeRatioTop9": [],
            "changeRatioBottom9": [],
            "speedRatioTop9": [
                {
                    "code": "510050", "name": "上证50ETF", "chgpct": 1.5,
                    "speedRatio": 0.0, "volumeRatio": 1.0, "etfLimitUpStockCnt": 0,
                    "topLeadStockCode": "", "topLeadStockName": "",
                    "topLeadStockChangeRatio": None,
                    "bottomLeadStockCode": "", "bottomLeadStockName": "",
                    "bottomLeadStockChangeRatio": None
                }
            ],
            "speedRatioBottom9": [],
            "volumeRatioTop9": [],
            "volumeRatioBottom9": [],
            "limitUpCountTop9": [],
            "limitUpCountBottom9": []
        })
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=data_with_mock):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        item = resp.json()["data"]["speedRatioTop9"][0]
        assert item["speedRatio"] == 0.0
        assert item["volumeRatio"] == 1.0

    def test_lead_stock_empty_string_passthrough(self):
        _clear_cache()
        data_with_empty_lead = json.dumps({
            "updateTime": 1717200000,
            "changeRatioTop9": [
                {
                    "code": "512880", "name": "证券ETF", "chgpct": 2.35,
                    "speedRatio": None, "volumeRatio": None, "etfLimitUpStockCnt": None,
                    "topLeadStockCode": "", "topLeadStockName": "",
                    "topLeadStockChangeRatio": None,
                    "bottomLeadStockCode": "", "bottomLeadStockName": "",
                    "bottomLeadStockChangeRatio": None
                }
            ],
            "changeRatioBottom9": [], "speedRatioTop9": [],
            "speedRatioBottom9": [], "volumeRatioTop9": [],
            "volumeRatioBottom9": [], "limitUpCountTop9": [],
            "limitUpCountBottom9": []
        })
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=data_with_empty_lead):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        item = resp.json()["data"]["changeRatioTop9"][0]
        assert item["topLeadStockCode"] == ""
        assert item["topLeadStockName"] == ""


class TestEightRanksStructure:
    def test_all_eight_rank_keys_present(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=None):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        data = resp.json()["data"]
        expected_keys = [
            "changeRatioTop9", "changeRatioBottom9",
            "speedRatioTop9", "speedRatioBottom9",
            "volumeRatioTop9", "volumeRatioBottom9",
            "limitUpCountTop9", "limitUpCountBottom9",
        ]
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"
            assert isinstance(data[key], list), f"{key} should be a list"

    def test_rank_item_structure(self):
        _clear_cache()
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=SAMPLE_RANK_JSON):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        item = resp.json()["data"]["changeRatioTop9"][0]
        expected_fields = [
            "code", "name", "chgpct", "speedRatio", "volumeRatio",
            "etfLimitUpStockCnt", "topLeadStockCode", "topLeadStockName",
            "topLeadStockChangeRatio", "bottomLeadStockCode",
            "bottomLeadStockName", "bottomLeadStockChangeRatio"
        ]
        for field in expected_fields:
            assert field in item, f"Missing field: {field}"


class TestShortList:
    def test_list_shorter_than_nine(self):
        _clear_cache()
        data_short = json.dumps({
            "updateTime": 1717200000,
            "changeRatioTop9": [
                {"code": "512880", "name": "证券ETF", "chgpct": 2.35, "speedRatio": None, "volumeRatio": None, "etfLimitUpStockCnt": None, "topLeadStockCode": None, "topLeadStockName": None, "topLeadStockChangeRatio": None, "bottomLeadStockCode": None, "bottomLeadStockName": None, "bottomLeadStockChangeRatio": None}
            ],
            "changeRatioBottom9": [],
            "speedRatioTop9": [],
            "speedRatioBottom9": [],
            "volumeRatioTop9": [],
            "volumeRatioBottom9": [],
            "limitUpCountTop9": [],
            "limitUpCountBottom9": []
        })
        with mock.patch("ifund_hq_project.router.redis_get_rank_data", return_value=data_short):
            resp = client.get("/api/v1/etf/plate-stat/rank")
        assert len(resp.json()["data"]["changeRatioTop9"]) == 1
