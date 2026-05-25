"""早盘宝 Mock 配置 — ETF计算样本、赛道映射、标签、权重。

Status markers: [verified] / [mock] / [default] / [pending]
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

# === Scoring Weights [default] ===
WEIGHT_HEAT = 0.50       # 热度
WEIGHT_MOMENTUM = 0.35   # 动量
WEIGHT_LIQUIDITY = 0.10  # 流动性
WEIGHT_LOW_VOL = 0.05    # 低波

# === Heat Factor Weights [default] ===
HEAT_SEARCH_WEIGHT = 0.55   # 搜索热度Z分数权重
HEAT_BUY_WEIGHT = 0.45      # 首购热度Z分数权重

# === Z-Score Window [default] ===
Z_SCORE_WINDOW = 20  # T-19 至 T 日，共 20 个交易日

# === Momentum Window [default] ===
MOMENTUM_T_MINUS_1 = 1
MOMENTUM_T_MINUS_5 = 5

# === Liquidity Window [default] ===
LIQUIDITY_WINDOW = 20  # 近20个可用交易日

# === Low-Vol Window [default] ===
LOW_VOL_WINDOW = 20       # 最近20个日收益率
LOW_VOL_PRICE_WINDOW = 22  # 需要22个交易日收盘价

# === Market Tag Threshold [default] ===
MARKET_TAG_THRESHOLD = -0.03  # 20日动量中位数 < -0.03 → 谨慎参与

# === Precision [default] ===
DISPLAY_DECIMALS = 2       # 前端展示精度
INTERNAL_PRECISION = 10    # 内部计算精度

# === Mock ETF Sample Pool [mock] — 100 ETFs ===
MOCK_ETF_POOL: list[dict] = [
    {"code": "510050", "name": "上证50ETF"},
    {"code": "510300", "name": "沪深300ETF"},
    {"code": "510500", "name": "中证500ETF"},
    {"code": "159915", "name": "创业板ETF"},
    {"code": "588000", "name": "科创50ETF"},
    {"code": "510880", "name": "红利ETF"},
    {"code": "512880", "name": "证券ETF"},
    {"code": "512010", "name": "医药ETF"},
    {"code": "159949", "name": "创业板50ETF"},
    {"code": "510180", "name": "上证180ETF"},
    {"code": "512100", "name": "中证1000ETF"},
    {"code": "159845", "name": "中证1000ETF易方达"},
    {"code": "510210", "name": "上证综指ETF"},
    {"code": "513100", "name": "纳指ETF"},
    {"code": "513050", "name": "中概互联ETF"},
    {"code": "159941", "name": "纳指ETF广发"},
    {"code": "510900", "name": "恒生ETF"},
    {"code": "513330", "name": "恒生互联ETF"},
    {"code": "159920", "name": "恒生ETF华夏"},
    {"code": "512660", "name": "军工ETF"},
    {"code": "512710", "name": "军工龙头ETF"},
    {"code": "159995", "name": "芯片ETF"},
    {"code": "512760", "name": "半导体ETF"},
    {"code": "516160", "name": "新能源ETF"},
    {"code": "159766", "name": "新能源车ETF"},
    {"code": "516510", "name": "云计算ETF"},
    {"code": "515050", "name": "5GETF"},
    {"code": "515790", "name": "光伏ETF"},
    {"code": "512800", "name": "银行ETF"},
    {"code": "512690", "name": "酒ETF"},
    {"code": "159928", "name": "消费ETF"},
    {"code": "510630", "name": "消费ETF华夏"},
    {"code": "512980", "name": "传媒ETF"},
    {"code": "516820", "name": "医疗ETF"},
    {"code": "512170", "name": "医疗ETF华宝"},
    {"code": "159883", "name": "医疗器械ETF"},
    {"code": "516190", "name": "新材料ETF"},
    {"code": "159755", "name": "电池ETF"},
    {"code": "512580", "name": "环保ETF"},
    {"code": "516880", "name": "电力ETF"},
    {"code": "159611", "name": "电力ETF广发"},
    {"code": "512400", "name": "有色ETF"},
    {"code": "159980", "name": "有色ETF建信"},
    {"code": "516150", "name": "稀土ETF"},
    {"code": "159865", "name": "养殖ETF"},
    {"code": "516780", "name": "畜牧ETF"},
    {"code": "159825", "name": "农业ETF"},
    {"code": "516970", "name": "基建ETF"},
    {"code": "516310", "name": "基建ETF易方达"},
    {"code": "512200", "name": "房地产ETF"},
    {"code": "159768", "name": "房地产ETF南方"},
    {"code": "516110", "name": "汽车ETF"},
    {"code": "516390", "name": "智能汽车ETF"},
    {"code": "515880", "name": "通信ETF"},
    {"code": "516520", "name": "软件ETF"},
    {"code": "159869", "name": "游戏ETF"},
    {"code": "516010", "name": "游戏ETF国泰"},
    {"code": "512670", "name": "国防ETF"},
    {"code": "159613", "name": "信息安全ETF"},
    {"code": "516500", "name": "大数据ETF"},
    {"code": "516000", "name": "金融科技ETF"},
    {"code": "159851", "name": "金融科技ETF华夏"},
    {"code": "515030", "name": "新能源车ETF华夏"},
    {"code": "516350", "name": "碳中和ETF"},
    {"code": "159790", "name": "碳中和ETF富国"},
    {"code": "159667", "name": "机床ETF"},
    {"code": "516630", "name": "机器人ETF"},
    {"code": "159770", "name": "机器人ETF华夏"},
    {"code": "516020", "name": "人工智能ETF"},
    {"code": "159819", "name": "人工智能ETF易方达"},
    {"code": "515210", "name": "钢铁ETF"},
    {"code": "516750", "name": "建材ETF"},
    {"code": "159745", "name": "建材ETF国泰"},
    {"code": "512560", "name": "旅游ETF"},
    {"code": "516590", "name": "家电ETF"},
    {"code": "159996", "name": "家电ETF国泰"},
    {"code": "516950", "name": "化工ETF"},
    {"code": "159870", "name": "化工ETF鹏华"},
    {"code": "516180", "name": "煤炭ETF"},
    {"code": "159930", "name": "能源ETF"},
    {"code": "516670", "name": "石化ETF"},
    {"code": "512530", "name": "黄金ETF"},
    {"code": "518880", "name": "黄金ETF华安"},
    {"code": "159934", "name": "黄金ETF易方达"},
    {"code": "511010", "name": "国债ETF"},
    {"code": "511260", "name": "十年国债ETF"},
    {"code": "511360", "name": "短融ETF"},
    {"code": "159649", "name": "同业存单ETF"},
    {"code": "513600", "name": "港股通ETF"},
    {"code": "159615", "name": "港股消费ETF"},
    {"code": "513130", "name": "恒生科技ETF"},
    {"code": "159742", "name": "恒生科技ETF博时"},
    {"code": "159636", "name": "港股通50ETF"},
    {"code": "159726", "name": "恒生红利ETF"},
    {"code": "159605", "name": "中概互联ETF广发"},
    {"code": "159607", "name": "中概互联ETF嘉实"},
    {"code": "159788", "name": "港股通100ETF"},
    {"code": "513060", "name": "恒生医疗ETF"},
    {"code": "159892", "name": "恒生医疗ETF博时"},
    {"code": "159610", "name": "碳中和50ETF"},
]


@dataclass
class MockHeatFieldConfig:
    """热度原始字段 Mock 配置 [mock].

    Leader 指派：sousuo_uv 等字段优先真实验证，不可取时 Mock。
    fund-indic-search-test 检索结果：全部 NO_MATCH → 使用 Mock。
    """

    sousuo_uv_mean: float = 5000.0
    sousuo_uv_std: float = 2000.0
    sousuo_click_uv_mean: float = 800.0
    sousuo_click_uv_std: float = 400.0
    fenshi_uv_mean: float = 3000.0
    fenshi_uv_std: float = 1500.0
    add_uv_mean: float = 200.0
    add_uv_std: float = 100.0
    buy_uv_mean: float = 50.0
    buy_uv_std: float = 30.0


@dataclass
class MockPriceConfig:
    """Mock 行情数据配置 [mock].

    用于模拟收盘价序列。实际应从 unitNav/adjNav 序列获取。
    收盘价范围：0.5 ~ 5.0 元
    """

    base_price_mean: float = 2.0
    base_price_std: float = 0.8
    daily_return_mean: float = 0.0002  # 日均收益率约 0.02%
    daily_return_std: float = 0.015    # 日波动约 1.5%


@dataclass
class MockTurnoverConfig:
    """Mock 成交额配置 [mock].

    turnover 指标状态为 deprecated，从行情接口取原始数据自行计算。
    本轮使用 Mock 数据。
    """

    turnover_mean: float = 500_000_000.0   # 日均成交额 5 亿
    turnover_std: float = 300_000_000.0


# === Mock 赛道映射表 [mock] — ETF code → 三级赛道 ===
MOCK_SECTOR_MAP: dict[str, str] = {
    "510050": "大盘宽基",
    "510300": "大盘宽基",
    "510500": "中盘宽基",
    "159915": "创业板宽基",
    "588000": "科创板宽基",
    "510880": "红利策略",
    "512880": "证券",
    "512010": "医药",
    "159949": "创业板宽基",
    "510180": "大盘宽基",
    "512100": "小盘宽基",
    "159845": "小盘宽基",
    "510210": "大盘宽基",
    "513100": "跨境-美股",
    "513050": "跨境-中概",
    "159941": "跨境-美股",
    "510900": "跨境-港股",
    "513330": "跨境-港股科技",
    "159920": "跨境-港股",
    "512660": "军工",
    "512710": "军工",
    "159995": "半导体",
    "512760": "半导体",
    "516160": "新能源",
    "159766": "新能源车",
    "516510": "科技-云计算",
    "516520": "科技-软件",
    "515050": "科技-5G",
    "515790": "新能源-光伏",
    "512800": "银行",
    "512690": "消费-白酒",
    "159928": "消费",
    "510630": "消费",
    "512980": "传媒",
    "516820": "医药",
    "512170": "医药",
    "159883": "医药-器械",
    "516190": "新材料",
    "159755": "新能源-电池",
    "512580": "环保",
    "516880": "电力",
    "159611": "电力",
    "512400": "有色",
    "159980": "有色",
    "516150": "稀土",
    "159865": "农业-养殖",
    "516780": "农业-畜牧",
    "159825": "农业",
    "516970": "基建",
    "516310": "基建",
    "512200": "房地产",
    "159768": "房地产",
    "516110": "汽车",
    "516390": "汽车-智能",
    "515880": "科技-通信",
    "159869": "传媒-游戏",
    "516010": "传媒-游戏",
    "512670": "军工-国防",
    "159613": "科技-信息安全",
    "516500": "科技-大数据",
    "516000": "科技-金融科技",
    "159851": "科技-金融科技",
    "515030": "新能源车",
    "516350": "碳中和",
    "159790": "碳中和",
    "159667": "制造-机床",
    "516630": "制造-机器人",
    "159770": "制造-机器人",
    "516020": "科技-AI",
    "159819": "科技-AI",
    "515210": "钢铁",
    "516750": "建材",
    "159745": "建材",
    "512560": "消费-旅游",
    "516590": "消费-家电",
    "159996": "消费-家电",
    "516950": "化工",
    "159870": "化工",
    "516180": "能源-煤炭",
    "159930": "能源",
    "516670": "能源-石化",
    "512530": "商品-黄金",
    "518880": "商品-黄金",
    "159934": "商品-黄金",
    "511010": "债券-国债",
    "511260": "债券-国债",
    "511360": "债券-短融",
    "159649": "债券-存单",
    "513600": "跨境-港股",
    "159615": "跨境-港股消费",
    "513130": "跨境-港股科技",
    "159742": "跨境-港股科技",
    "159636": "跨境-港股",
    "159726": "跨境-港股红利",
    "159605": "跨境-中概",
    "159607": "跨境-中概",
    "159788": "跨境-港股",
    "513060": "跨境-港股医药",
    "159892": "跨境-港股医药",
    "159610": "碳中和",
}

# === Mock 个基标签 [mock] ===
MOCK_ETF_TAGS: dict[str, list[str]] = {
    "510050": ["大盘蓝筹", "低估值", "高分红"],
    "510300": ["核心资产", "大盘均衡"],
    "510500": ["中盘成长", "弹性较好"],
    "159915": ["创业板", "高成长"],
    "588000": ["科技创新", "硬科技"],
    "510880": ["高股息", "防御配置"],
    "512880": ["券商", "周期敏感"],
    "512010": ["医药龙头", "长牛赛道"],
    "159949": ["创业板龙头", "高弹性"],
}

MOCK_DEFAULT_TAGS: list[str] = ["ETF", "指数基金"]


# === Database Config [default] ===
DB_PATH = "morning_report.db"


# === Scheduler Config [default] ===
# 定时计算触发时间：每个交易日早上 7:00
SCHEDULE_HOUR = 7
SCHEDULE_MINUTE = 0

# === Cache Config [default] ===
CACHE_TTL_SECONDS = 300  # 5 分钟
