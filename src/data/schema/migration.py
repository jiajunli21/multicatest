"""数据库 Schema 与 Migration。[default]

使用 SQLite 作为存储引擎。所有时间口径暂按自然日模拟 [pending: 交易日口径]。
"""

import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data_db")
DB_PATH = os.path.join(DB_DIR, "morning_report.db")

SCHEMA_VERSION = 1

DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS etf_samples (
        code TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL DEFAULT 'ETF',
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS etf_daily_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etf_code TEXT NOT NULL,
        date TEXT NOT NULL,
        close_price REAL,          -- [verified] 来源: unitNav/adjNav
        turnover REAL,              -- [default] 成交额, Mock数据
        sousuo_uv REAL,             -- [mock] 搜索UV
        sousuo_click_uv REAL,       -- [mock] 搜索点击UV
        fenshi_uv REAL,             -- [mock] 分时UV
        add_uv REAL,                -- [mock] 加自选UV
        buy_uv REAL,                -- [mock] 购买UV
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(etf_code, date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS etf_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etf_code TEXT NOT NULL,
        date TEXT NOT NULL,
        search_heat_z REAL,         -- [mock] 搜索热度Z分数
        first_buy_heat_z REAL,      -- [mock] 首购热度Z分数
        heat_factor REAL,           -- [mock] 热度因子 = 0.55*搜索热度Z + 0.45*首购热度Z
        momentum_factor REAL,       -- [default] 动量因子 = C_t-1/C_t-5 - 1
        liquidity_factor REAL,      -- [default] 流动性因子 = 20日成交额均值
        lowvol_factor REAL,         -- [default] 低波因子 = std(20个日收益率)
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(etf_code, date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS etf_rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etf_code TEXT NOT NULL,
        date TEXT NOT NULL,
        heat_rank INTEGER,           -- 热度排名 (DESC)
        momentum_rank INTEGER,       -- 动量排名 (DESC)
        liquidity_rank INTEGER,      -- 流动性排名 (DESC)
        lowvol_rank INTEGER,         -- 低波排名 (ASC)
        heat_rank_score REAL,        -- 热度排名分数
        momentum_rank_score REAL,    -- 动量排名分数
        liquidity_rank_score REAL,   -- 流动性排名分数
        lowvol_rank_score REAL,      -- 低波排名分数
        composite_score REAL,        -- ETF综合评分 (50%*热度 + 35%*动量 + 10%*流动性 + 5%*低波)
        overall_rank INTEGER,        -- 综合排名 (DESC)
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(etf_code, date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS etf_labels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        etf_code TEXT NOT NULL,
        date TEXT NOT NULL,
        market_tag TEXT,             -- [default] 谨慎参与/积极参与 (基于20日动量中位数)
        momentum_median_20d REAL,    -- 20日动量中位数
        fund_tags TEXT,              -- [mock] 个基标签 JSON数组
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(etf_code, date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS etf_sector_mapping (
        etf_code TEXT PRIMARY KEY,
        sector_name TEXT NOT NULL,   -- [mock] 三级赛道名称
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS etf_history_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        etf_code TEXT NOT NULL,
        composite_score REAL,
        overall_rank INTEGER,
        signal_3d_return REAL,       -- 信号后3日涨幅, 不足3交易日为NULL
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        UNIQUE(date, etf_code)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mock_news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        summary TEXT,
        publish_time TEXT NOT NULL,
        source TEXT DEFAULT '同花顺',
        url TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT (datetime('now')),
        description TEXT
    )
    """,
]


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def migrate(db_path: str = DB_PATH):
    conn = get_connection(db_path)
    try:
        # 检查 schema_version 表是否存在，兼容首次运行
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
        ).fetchone()
        if table_exists:
            current = conn.execute(
                "SELECT MAX(version) FROM schema_version"
            ).fetchone()[0] or 0
            if current >= SCHEMA_VERSION:
                return
        else:
            current = 0

        for stmt in DDL_STATEMENTS:
            conn.execute(stmt)

        conn.execute(
            "INSERT OR REPLACE INTO schema_version (version, description) VALUES (?, ?)",
            (SCHEMA_VERSION, "早盘宝数据初始化"),
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
