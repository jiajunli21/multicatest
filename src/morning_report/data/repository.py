"""数据访问层 — SQLite 存储，Repository/DAO 模式。

Status: [default]
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from ..config import DB_PATH
from ..models import ETFScore, HistoricalRecord


def get_db_path() -> Path:
    """获取数据库文件路径。"""
    import os
    # 尝试从环境变量获取 git root，否则使用当前目录
    git_root = os.environ.get("GIT_ROOT", "")
    if git_root:
        base = Path(git_root)
    else:
        base = Path.cwd()
    return base / DB_PATH


@contextmanager
def get_connection():
    """获取数据库连接（自动提交/关闭）。"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化数据库表结构 [default]."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS etf_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calc_date TEXT NOT NULL,
                etf_code TEXT NOT NULL,
                etf_name TEXT NOT NULL,
                heat_rank_score REAL NOT NULL,
                momentum_rank_score REAL NOT NULL,
                liquidity_rank_score REAL NOT NULL,
                low_vol_rank_score REAL NOT NULL,
                composite_score REAL NOT NULL,
                rank INTEGER NOT NULL,
                sector TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                market_tag TEXT DEFAULT '',
                status TEXT DEFAULT 'success',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(calc_date, etf_code)
            );

            CREATE INDEX IF NOT EXISTS idx_etf_scores_date
                ON etf_scores(calc_date);

            CREATE INDEX IF NOT EXISTS idx_etf_scores_rank
                ON etf_scores(calc_date, rank);

            CREATE TABLE IF NOT EXISTS historical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                etf_code TEXT NOT NULL,
                etf_name TEXT NOT NULL,
                composite_score REAL NOT NULL,
                rank INTEGER NOT NULL,
                signal_3d_return REAL,
                current_return REAL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(record_date, etf_code)
            );

            CREATE INDEX IF NOT EXISTS idx_historical_date
                ON historical_records(record_date);
        """)


def save_etf_scores(scores: list[ETFScore]):
    """保存 ETF 评分结果（幂等：相同 calc_date + etf_code 覆盖）."""
    with get_connection() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO etf_scores
                (calc_date, etf_code, etf_name,
                 heat_rank_score, momentum_rank_score,
                 liquidity_rank_score, low_vol_rank_score,
                 composite_score, rank, sector, tags,
                 market_tag, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, [
            (
                s.calc_date.isoformat(), s.etf_code, s.etf_name,
                s.heat_rank_score, s.momentum_rank_score,
                s.liquidity_rank_score, s.low_vol_rank_score,
                s.composite_score, s.rank,
                s.sector, json.dumps(s.tags, ensure_ascii=False),
                s.market_tag.value if s.market_tag else "",
                s.status.value,
            )
            for s in scores
        ])


def get_etf_scores(calc_date: date) -> list[dict]:
    """查询指定日期的 ETF 评分（按 rank ASC）."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM etf_scores WHERE calc_date = ? ORDER BY rank ASC",
            (calc_date.isoformat(),)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["tags"] = json.loads(d.get("tags", "[]"))
            result.append(d)
        return result


def get_top5_scores(calc_date: date) -> list[dict]:
    """查询指定日期的 Top5 ETF 评分."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM etf_scores WHERE calc_date = ? ORDER BY rank ASC LIMIT 5",
            (calc_date.isoformat(),)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["tags"] = json.loads(d.get("tags", "[]"))
            result.append(d)
        return result


def save_historical_records(records: list[HistoricalRecord]):
    """保存历史表现记录."""
    with get_connection() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO historical_records
                (record_date, etf_code, etf_name, composite_score,
                 rank, signal_3d_return, current_return, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, [
            (
                r.date.isoformat(), r.etf_code, r.etf_name,
                r.composite_score, r.rank,
                r.signal_3d_return, r.current_return,
            )
            for r in records
        ])


def get_historical_records(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    """查询历史表现记录."""
    with get_connection() as conn:
        query = "SELECT * FROM historical_records WHERE 1=1"
        params = []
        if start_date:
            query += " AND record_date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND record_date <= ?"
            params.append(end_date.isoformat())
        query += " ORDER BY record_date DESC, rank ASC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
