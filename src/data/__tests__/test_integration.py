"""集成测试：端到端每日任务流程。"""

import json
import os
import tempfile
import unittest

from src.data.schema.migration import migrate, get_connection
from src.data.models.data_access import (
    get_rankings_by_date,
    get_labels_by_date,
    get_history_scores,
    get_mock_news,
)
from src.data.scheduler.daily_job import run_daily_job, generate_mock_daily_data


class TestMockDataGeneration(unittest.TestCase):
    def test_deterministic(self):
        records1 = generate_mock_daily_data("510050", "2026-05-25", 22)
        records2 = generate_mock_daily_data("510050", "2026-05-25", 22)
        self.assertEqual(len(records1), 22)
        self.assertEqual(records1, records2)

    def test_different_code_diff_data(self):
        r1 = generate_mock_daily_data("510050", "2026-05-25", 5)
        r2 = generate_mock_daily_data("510300", "2026-05-25", 5)
        self.assertNotEqual(r1, r2)


def _make_configs(tmpdir):
    """创建最小测试配置。"""
    samples = {
        "status": "[mock]",
        "etfs": [
            {"code": "510050", "name": "上证50ETF", "type": "股票型"},
            {"code": "510300", "name": "沪深300ETF", "type": "股票型"},
            {"code": "510500", "name": "中证500ETF", "type": "股票型"},
            {"code": "159915", "name": "创业板ETF", "type": "股票型"},
            {"code": "588000", "name": "科创50ETF", "type": "股票型"},
        ],
    }
    sector = {"mapping": {"510050": "大盘价值", "510300": "大盘均衡", "510500": "中盘成长", "159915": "创业板成长", "588000": "科创成长"}}
    tags = {"etf_tags": {"510050": ["低估值"], "510300": ["龙头"]}}
    news = {"news": [{"title": "测试新闻", "summary": "摘要", "publish_time": "2026-05-25 08:00:00", "source": "同花顺", "url": "http://t.cn/1"}]}

    for name, data in [("etf_samples.json", samples), ("sector_mapping.json", sector), ("fund_tags.json", tags), ("mock_news.json", news)]:
        with open(os.path.join(tmpdir, name), "w") as f:
            json.dump(data, f)


class TestDailyJob(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp()
        _make_configs(self._tmpdir)

    def test_end_to_end(self):
        result = run_daily_job("2026-05-25", self._tmpdir)
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["date"], "2026-05-25")
        self.assertEqual(result["etf_count"], 5)
        self.assertGreater(len(result["top5"]), 0)

    def test_top5_sorting(self):
        result = run_daily_job("2026-05-25", self._tmpdir)
        top5 = result["top5"]
        for i in range(len(top5) - 1):
            self.assertLessEqual(top5[i]["overall_rank"], top5[i + 1]["overall_rank"])

    def test_idempotency(self):
        r1 = run_daily_job("2026-05-25", self._tmpdir)
        r2 = run_daily_job("2026-05-25", self._tmpdir)
        self.assertEqual(r1["status"], r2["status"])
        self.assertEqual(r1["etf_count"], r2["etf_count"])
        scores1 = {e["etf_code"]: e["composite_score"] for e in r1["top5"]}
        scores2 = {e["etf_code"]: e["composite_score"] for e in r2["top5"]}
        self.assertEqual(scores1, scores2)

    def test_rankings_stored(self):
        run_daily_job("2026-05-25", self._tmpdir)
        conn = get_connection()
        try:
            rankings = get_rankings_by_date(conn, "2026-05-25")
            self.assertEqual(len(rankings), 5)
            for r in rankings:
                self.assertGreaterEqual(r["composite_score"], 0.0)
                self.assertLessEqual(r["composite_score"], 1.0)
        finally:
            conn.close()

    def test_labels_stored(self):
        run_daily_job("2026-05-25", self._tmpdir)
        conn = get_connection()
        try:
            labels = get_labels_by_date(conn, "2026-05-25")
            self.assertEqual(len(labels), 5)
            for l in labels:
                self.assertIn(l["market_tag"], ["积极参与", "谨慎参与"])
        finally:
            conn.close()

    def test_history_stored(self):
        run_daily_job("2026-05-25", self._tmpdir)
        conn = get_connection()
        try:
            history = get_history_scores(conn)
            self.assertGreater(len(history), 0)
        finally:
            conn.close()

    def test_news_loaded(self):
        run_daily_job("2026-05-25", self._tmpdir)
        conn = get_connection()
        try:
            news = get_mock_news(conn)
            self.assertGreater(len(news), 0)
        finally:
            conn.close()

    def test_score_range(self):
        result = run_daily_job("2026-05-25", self._tmpdir)
        for etf in result["top5"]:
            self.assertGreaterEqual(etf["composite_score"], 0.0)
            self.assertLessEqual(etf["composite_score"], 1.0)


if __name__ == "__main__":
    unittest.main()
