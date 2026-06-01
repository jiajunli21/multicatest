"""BlockStatEtfTabTask 配置常量。

speedRatio/volumeRatio 为软阻塞项，当前以 Mock 常量占位。
待扶摇接口确认后，将 MOCK 常量和 *_FETCH_ENABLED 替换为真实拉取逻辑。
"""

# Redis
REDIS_KEY = "plateStatEtf:rank:data"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 基金池接口
FUND_POOL_URL = "/quotation/fund_pool/v2/query"
FUND_POOL_UNIQUE_TYPE = "etf_third_level_track_list"

# 扶摇 ETF 行情接口（路径待确认）
FUYAO_ETF_QUOTE_URL = "/quotation/data/query/v1/table"

# 成分股关系接口
STOCK_RELATION_URL = "/quotation/data/query/v1/relation"
STOCK_RELATION_TYPE = "stock_etf_subred"
MARKET_FILTER = [17, 33, 177]

# 三市场全量股票涨幅接口（路径待确认）
ALL_MARKET_STOCK_URL = "/quotation/data/query/v1/table"

# 榜单配置
TOP_N = 9
BOTTOM_N = 9
SORT_DIRECTIONS = ["DESC", "ASC"]

# 排序维度
DIMENSIONS = {
    "changeRatio": {"name": "涨幅", "field": "chgpct", "unit": "%"},
    "speedRatio": {"name": "涨速", "field": "speedRatio", "unit": "%"},
    "volumeRatio": {"name": "量比", "field": "volumeRatio", "unit": ""},
    "limitUpCount": {"name": "涨停数", "field": "etfLimitUpStockCnt", "unit": "个"},
}

# ---- 软阻塞项 Mock 配置 ----
# 待扶摇接口确认后替换为实际数据源

# speedRatio/volumeRatio Mock 常量（扩展点：改为从扶摇接口获取真实值）
MOCK_SPEED_RATIO = 0.0
MOCK_VOLUME_RATIO = 1.0

# 是否启用扶摇涨速/量比真实拉取（扩展点：接口确认后改为 True）
SPEED_RATIO_FETCH_ENABLED = False
VOLUME_RATIO_FETCH_ENABLED = False

# 是否启用三市场全量股票涨幅拉取（扩展点：接口确认后改为 True）
ALL_MARKET_STOCK_FETCH_ENABLED = False
