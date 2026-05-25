"""早盘宝数据模型定义。

Status: [default] for schema, [mock] for data sources.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class MarketTag(str, Enum):
    CAUTIOUS = "谨慎参与"
    ACTIVE = "积极参与"


class DataSource(str, Enum):
    VERIFIED = "verified"
    MOCK = "mock"
    DEFAULT = "default"
    PENDING = "pending"


class CalcStatus(str, Enum):
    SUCCESS = "success"
    INSUFFICIENT_SAMPLE = "insufficient_sample"
    NOT_CALCULABLE = "not_calculable"  # 停牌、无数据等


@dataclass
class ETFInfo:
    """ETF 基本信息."""
    code: str
    name: str
    sector: str = ""          # 三级赛道 [mock]
    tags: list[str] = field(default_factory=list)  # 个基标签 [mock]


@dataclass
class HeatRawFields:
    """热度原始字段 (T 日).

    sousuo_uv 等字段 fund-indic-search-test 全部 NO_MATCH → [mock].
    """
    date: date
    etf_code: str
    sousuo_uv: float = 0.0
    sousuo_click_uv: float = 0.0
    fenshi_uv: float = 0.0
    add_uv: float = 0.0
    buy_uv: float = 0.0
    source: DataSource = DataSource.MOCK


@dataclass
class DailyPrice:
    """日行情数据（收盘价/净值）.

    收盘价来源：unitNav/adjNav [verified].
    实际从行情接口拉取，本轮使用 Mock 数据模拟 [mock].
    """
    date: date
    etf_code: str
    close_price: float       # 收盘价（或单位净值替代）
    turnover: float = 0.0    # 成交额（元）[default] — 从行情接口取原始数据
    source: DataSource = DataSource.MOCK


@dataclass
class HeatFactorResult:
    """热度因子计算结果."""
    etf_code: str
    calc_date: date
    search_heat_t: float          # T日搜索热度 = log(1+sousuo_uv+3*sousuo_click_uv)
    buy_heat_t: float              # T日首购热度 = log(1+fenshi_uv+5*add_uv+20*buy_uv)
    search_heat_z: float           # 搜索热度Z分数
    buy_heat_z: float              # 首购热度Z分数
    heat_factor: float             # 热度因子 = 0.55*搜索Z + 0.45*首购Z
    status: CalcStatus = CalcStatus.SUCCESS
    source: DataSource = DataSource.MOCK


@dataclass
class MomentumFactorResult:
    """动量因子计算结果."""
    etf_code: str
    calc_date: date
    c_t_minus_1: float    # T-1 日收盘价
    c_t_minus_5: float    # T-5 日收盘价
    momentum_factor: float  # C_t-1/C_t-5 - 1
    status: CalcStatus = CalcStatus.SUCCESS
    source: DataSource = DataSource.DEFAULT


@dataclass
class LiquidityFactorResult:
    """流动性因子计算结果."""
    etf_code: str
    calc_date: date
    avg_turnover_20d: float  # 近20个可用交易日成交额均值 [default]
    status: CalcStatus = CalcStatus.SUCCESS
    sample_count: int = 20
    source: DataSource = DataSource.DEFAULT


@dataclass
class LowVolFactorResult:
    """低波因子计算结果."""
    etf_code: str
    calc_date: date
    daily_returns: list[float] = field(default_factory=list)  # 最近20个日收益率
    low_vol_factor: float = 0.0   # std(20个日收益率) [ASC]
    status: CalcStatus = CalcStatus.SUCCESS
    source: DataSource = DataSource.DEFAULT


@dataclass
class RankScore:
    """排名分数."""
    etf_code: str
    raw_value: float       # 原始因子值
    rank: int              # 排名 (1-based)
    total_count: int       # 参与排名总数
    rank_score: float      # (total - rank) / total
    status: CalcStatus = CalcStatus.SUCCESS  # 原始因子计算状态


@dataclass
class ETFScore:
    """ETF 综合评分."""
    etf_code: str
    etf_name: str
    calc_date: date
    heat_rank_score: float      # 热度排名分数
    momentum_rank_score: float  # 动量排名分数
    liquidity_rank_score: float  # 流动性排名分数
    low_vol_rank_score: float   # 低波排名分数
    composite_score: float      # 综合评分 = 加权求和
    rank: int                   # 综合排名 (1-based, DESC)
    sector: str = ""            # 三级赛道 [mock]
    tags: list[str] = field(default_factory=list)  # 个基标签 [mock]
    market_tag: Optional[MarketTag] = None  # 谨慎参与/积极参与 [default]
    status: CalcStatus = CalcStatus.SUCCESS


@dataclass
class Top5Result:
    """Top5 推荐结果."""
    top_etfs: list[ETFScore]            # Top5 ETF 列表
    sectors: list[dict]                 # 赛道分布 [{name, etfs: [...]}]
    signal_date: date                   # 样本信号日
    market_tag: str                     # 谨慎参与/积极参与
    update_time: datetime               # 数据更新时间
    total_etf_count: int               # 计算样本总数


@dataclass
class HistoricalRecord:
    """历史表现记录."""
    date: date
    etf_code: str
    etf_name: str
    composite_score: float
    rank: int
    signal_3d_return: Optional[float] = None  # 信号后3日涨幅，不足3交易日为None
    current_return: Optional[float] = None    # 当前涨幅


@dataclass
class NewsItem:
    """资讯条目 [mock]."""
    title: str
    summary: str
    time: datetime
    source: str
    url: str = ""


@dataclass
class GuideContent:
    """指南内容 [mock]."""
    content: str
    update_time: datetime
