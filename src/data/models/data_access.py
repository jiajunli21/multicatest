"""数据访问层：ETF样本、日线数据、因子、排名、标签、历史、资讯的读写操作。

所有写操作支持幂等 (INSERT OR REPLACE / ON CONFLICT UPDATE)。
事务策略：批量写入使用单事务，读取使用WAL模式。
"""

import json
import sqlite3
from typing import Optional

from src.data.schema.migration import get_connection


# ---- ETF Samples (AD-001) ----

def load_etf_samples(conn: sqlite3.Connection, samples: list):
    """批量写入ETF计算样本。[mock]"""
    conn.executemany(
        """INSERT OR REPLACE INTO etf_samples (code, name, type, updated_at)
           VALUES (?, ?, ?, datetime('now'))""",
        [(s["code"], s["name"], s.get("type", "ETF")) for s in samples],
    )
    conn.commit()


def get_active_etf_samples(conn: sqlite3.Connection) -> list:
    """获取活跃ETF样本列表。"""
    rows = conn.execute(
        "SELECT code, name, type FROM etf_samples WHERE status='active' ORDER BY code"
    ).fetchall()
    return [dict(r) for r in rows]


# ---- ETF Daily Data (DI-001/002/003) ----

def upsert_daily_data(conn: sqlite3.Connection, records: list):
    """批量写入/更新ETF日线数据。幂等：UNIQUE(etf_code, date)。"""
    conn.executemany(
        """INSERT INTO etf_daily_data
           (etf_code, date, close_price, turnover, sousuo_uv, sousuo_click_uv,
            fenshi_uv, add_uv, buy_uv)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(etf_code, date) DO UPDATE SET
             close_price=excluded.close_price,
             turnover=excluded.turnover,
             sousuo_uv=excluded.sousuo_uv,
             sousuo_click_uv=excluded.sousuo_click_uv,
             fenshi_uv=excluded.fenshi_uv,
             add_uv=excluded.add_uv,
             buy_uv=excluded.buy_uv,
             created_at=datetime('now')""",
        records,
    )
    conn.commit()


def get_daily_data_window(
    conn: sqlite3.Connection, etf_code: str, end_date: str, window_size: int = 22
) -> list:
    """获取指定ETF的最近window_size个交易日日线数据。

    Returns:
        [{etf_code, date, close_price, turnover, sousuo_uv, ...}, ...] 按date降序
    """
    rows = conn.execute(
        """SELECT * FROM etf_daily_data
           WHERE etf_code = ? AND date <= ?
           ORDER BY date DESC
           LIMIT ?""",
        (etf_code, end_date, window_size),
    ).fetchall()
    return [dict(r) for r in rows]


# ---- ETF Factors (DI-004~DI-009) ----

def upsert_factors(conn: sqlite3.Connection, records: list):
    """批量写入ETF因子数据。幂等：UNIQUE(etf_code, date)。"""
    conn.executemany(
        """INSERT INTO etf_factors
           (etf_code, date, search_heat_z, first_buy_heat_z, heat_factor,
            momentum_factor, liquidity_factor, lowvol_factor)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(etf_code, date) DO UPDATE SET
             search_heat_z=excluded.search_heat_z,
             first_buy_heat_z=excluded.first_buy_heat_z,
             heat_factor=excluded.heat_factor,
             momentum_factor=excluded.momentum_factor,
             liquidity_factor=excluded.liquidity_factor,
             lowvol_factor=excluded.lowvol_factor,
             created_at=datetime('now')""",
        records,
    )
    conn.commit()


def get_factors_by_date(conn: sqlite3.Connection, date: str) -> list:
    """获取指定日期的所有ETF因子数据。"""
    rows = conn.execute(
        "SELECT * FROM etf_factors WHERE date = ?", (date,)
    ).fetchall()
    return [dict(r) for r in rows]


# ---- ETF Rankings (DI-010) ----

def upsert_rankings(conn: sqlite3.Connection, records: list):
    """批量写入ETF排名数据。幂等：UNIQUE(etf_code, date)。"""
    conn.executemany(
        """INSERT INTO etf_rankings
           (etf_code, date, heat_rank, momentum_rank, liquidity_rank, lowvol_rank,
            heat_rank_score, momentum_rank_score, liquidity_rank_score,
            lowvol_rank_score, composite_score, overall_rank)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(etf_code, date) DO UPDATE SET
             heat_rank=excluded.heat_rank,
             momentum_rank=excluded.momentum_rank,
             liquidity_rank=excluded.liquidity_rank,
             lowvol_rank=excluded.lowvol_rank,
             heat_rank_score=excluded.heat_rank_score,
             momentum_rank_score=excluded.momentum_rank_score,
             liquidity_rank_score=excluded.liquidity_rank_score,
             lowvol_rank_score=excluded.lowvol_rank_score,
             composite_score=excluded.composite_score,
             overall_rank=excluded.overall_rank,
             created_at=datetime('now')""",
        records,
    )
    conn.commit()


def get_rankings_by_date(conn: sqlite3.Connection, date: str) -> list:
    """获取指定日期排名，按综合排名升序。"""
    rows = conn.execute(
        """SELECT r.*, s.name as etf_name, s.type as etf_type
           FROM etf_rankings r
           LEFT JOIN etf_samples s ON r.etf_code = s.code
           WHERE r.date = ?
           ORDER BY r.overall_rank ASC""",
        (date,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_top_n_rankings(conn: sqlite3.Connection, date: str, n: int = 5) -> list:
    """获取Top N ETF排名。"""
    rows = conn.execute(
        """SELECT r.*, s.name as etf_name, s.type as etf_type
           FROM etf_rankings r
           LEFT JOIN etf_samples s ON r.etf_code = s.code
           WHERE r.date = ?
           ORDER BY r.overall_rank ASC
           LIMIT ?""",
        (date, n),
    ).fetchall()
    return [dict(r) for r in rows]


# ---- ETF Labels (AD-008/009) ----

def upsert_labels(conn: sqlite3.Connection, records: list):
    """批量写入ETF标签。幂等：UNIQUE(etf_code, date)。"""
    conn.executemany(
        """INSERT INTO etf_labels
           (etf_code, date, market_tag, momentum_median_20d, fund_tags)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(etf_code, date) DO UPDATE SET
             market_tag=excluded.market_tag,
             momentum_median_20d=excluded.momentum_median_20d,
             fund_tags=excluded.fund_tags,
             created_at=datetime('now')""",
        records,
    )
    conn.commit()


def get_labels_by_date(conn: sqlite3.Connection, date: str) -> list:
    """获取指定日期所有ETF标签。"""
    rows = conn.execute(
        "SELECT * FROM etf_labels WHERE date = ?", (date,)
    ).fetchall()
    return [dict(r) for r in rows]


# ---- Sector Mapping (DI-011) ----

def load_sector_mapping(conn: sqlite3.Connection, mapping: dict):
    """加载Mock赛道映射。[mock]"""
    conn.executemany(
        """INSERT OR REPLACE INTO etf_sector_mapping (etf_code, sector_name, created_at)
           VALUES (?, ?, datetime('now'))""",
        [(code, sector) for code, sector in mapping.items()],
    )
    conn.commit()


def get_sector_mapping(conn: sqlite3.Connection, etf_codes: Optional[list] = None) -> dict:
    """获取ETF赛道映射。"""
    if etf_codes:
        placeholders = ",".join("?" for _ in etf_codes)
        rows = conn.execute(
            f"SELECT etf_code, sector_name FROM etf_sector_mapping WHERE etf_code IN ({placeholders})",
            etf_codes,
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT etf_code, sector_name FROM etf_sector_mapping"
        ).fetchall()
    return {r["etf_code"]: r["sector_name"] for r in rows}


# ---- Historical Scores (DI-014) ----

def insert_history_scores(conn: sqlite3.Connection, records: list):
    """写入历史ETF分数。幂等：UNIQUE(date, etf_code)。"""
    conn.executemany(
        """INSERT INTO etf_history_scores (date, etf_code, composite_score, overall_rank)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(date, etf_code) DO UPDATE SET
             composite_score=excluded.composite_score,
             overall_rank=excluded.overall_rank,
             created_at=datetime('now')""",
        records,
    )
    conn.commit()


def get_history_scores(
    conn: sqlite3.Connection, etf_code: Optional[str] = None, limit: int = 30
) -> list:
    """查询历史ETF分数。

    Args:
        etf_code: 指定ETF代码或None(全部)
        limit: 最大返回天数
    """
    if etf_code:
        rows = conn.execute(
            """SELECT * FROM etf_history_scores
               WHERE etf_code = ?
               ORDER BY date DESC LIMIT ?""",
            (etf_code, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM etf_history_scores
               ORDER BY date DESC, overall_rank ASC LIMIT ?""",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]


# ---- Mock News (AD-010) ----

def load_mock_news(conn: sqlite3.Connection, news_items: list):
    """加载Mock资讯数据。[mock]"""
    conn.execute("DELETE FROM mock_news")
    conn.executemany(
        """INSERT INTO mock_news (title, summary, publish_time, source, url)
           VALUES (?, ?, ?, ?, ?)""",
        [(n["title"], n["summary"], n["publish_time"], n["source"], n["url"])
         for n in news_items],
    )
    conn.commit()


def get_mock_news(conn: sqlite3.Connection, limit: int = 20, offset: int = 0) -> list:
    """获取Mock资讯列表。"""
    rows = conn.execute(
        """SELECT * FROM mock_news
           ORDER BY publish_time DESC LIMIT ? OFFSET ?""",
        (limit, offset),
    ).fetchall()
    return [dict(r) for r in rows]
