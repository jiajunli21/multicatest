# ETF Tab C端业务接口契约

## 接口概览

- **路径**: `/quotation/plate_stat/etf_tab/v1/rank`
- **方法**: `GET`
- **说明**: 返回板块统计 ETF tab 的4个排序项（涨幅/涨速/量比/涨停数）各前9/后9共8份榜单数据及领涨/领跌成分股信息

## 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| rankType | String | 否 | 无（返回全部8份榜单） | 筛选单个排序项: `changeRatio` / `speedRatio` / `volumeRatio` / `limitUpCount` |

### 参数约束

- `rankType` 不在允许值集合内时返回 `code=400` 错误响应

## 请求示例

```bash
# 返回全部8份榜单
GET /quotation/plate_stat/etf_tab/v1/rank

# 仅返回涨幅前9/后9
GET /quotation/plate_stat/etf_tab/v1/rank?rankType=changeRatio
```

## 响应结构

所有响应使用统一信封: `{ code, message, data, timestamp }`

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "changeRatioTop9": [...],
    "changeRatioBottom9": [...],
    "speedRatioTop9": [...],
    "speedRatioBottom9": [...],
    "volumeRatioTop9": [...],
    "volumeRatioBottom9": [...],
    "limitUpCountTop9": [...],
    "limitUpCountBottom9": [...],
    "calcTimestamp": 1717200000000,
    "calcDate": "2026-06-01"
  },
  "timestamp": 1717200000000
}
```

### 榜单条目字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| stockCode | String | ETF代码 |
| marketCode | String | 市场代码 (17/33/177) |
| name | String | ETF名称 |
| tradeCode | String | 交易代码（展示用） |
| rankType | String | 排序类型: changeRatio/speedRatio/volumeRatio/limitUpCount |
| rankValue | BigDecimal | 排序值（涨幅/涨速/量比保留2位小数，涨停数为整数） |
| rank | Integer | 排名（从1开始） |
| rankOrder | String | 排序方向: DESC/ASC |
| topLeadStockCode | String | 领涨股票代码（成分股涨幅前9第一只） |
| topLeadStockName | String | 领涨股票名称 |
| topLeadStockChangeRatio | BigDecimal | 领涨股票涨幅（保留2位小数） |
| topLeadStockHoldRate | BigDecimal | 领涨股票持仓占比 |
| bottomLeadStockCode | String | 领跌股票代码（成分股涨幅后9第一只） |
| bottomLeadStockName | String | 领跌股票名称 |
| bottomLeadStockChangeRatio | BigDecimal | 领跌股票涨幅（保留2位小数） |
| bottomLeadStockHoldRate | BigDecimal | 领跌股票持仓占比 |

### 示例响应（涨幅前9中的单条记录）

```json
{
  "stockCode": "510050",
  "marketCode": "17",
  "name": "华夏上证50ETF",
  "tradeCode": "510050",
  "rankType": "changeRatio",
  "rankValue": 2.35,
  "rank": 1,
  "rankOrder": "DESC",
  "topLeadStockCode": "600519",
  "topLeadStockName": "贵州茅台",
  "topLeadStockChangeRatio": 5.20,
  "topLeadStockHoldRate": 15.30,
  "bottomLeadStockCode": "601318",
  "bottomLeadStockName": "中国平安",
  "bottomLeadStockChangeRatio": -1.20,
  "bottomLeadStockHoldRate": 8.50
}
```

## 错误响应

### 无效 rankType

```json
{
  "code": 400,
  "message": "Invalid rankType: xxx. Allowed: [limitUpCount, changeRatio, speedRatio, volumeRatio]",
  "data": null,
  "timestamp": 1717200000000
}
```

## 空态与降级

| 场景 | 行为 |
|------|------|
| Redis 和 Caffeine 均未命中 | 返回 `code=200`，`data` 中8个榜单均为空数组 `[]` |
| Redis 命中但部分榜单为空 | 对应榜单返回空数组 |
| Redis 读取异常 | 降级返回空榜单结构 (`code=200`) |
| 指定 rankType 但对应榜单为空 | 返回空数组 |

## 权限规则

- 流程验证版：无登录态校验，无行情权限校验

## 缓存策略

| 层级 | 配置 | 说明 |
|------|------|------|
| Caffeine (L1) | TTL 30s, max 100, LRU | 本地缓存，优先读取 |
| Redis (L2) | TTL 120s (由定时任务写入) | 回源缓存，Caffeine未命中时读取并回填 |

## 数据来源

- Redis key: `plateStatEtf:rank:data`
- 数据由定时任务 `BlockStatEtfTabTask` 每分钟写入
- 本接口不实时回源基金池/扶摇/成分股接口

## 生产技术栈

- 语言: Java 17
- 框架: Spring Boot 3.2
- 缓存: Caffeine + Spring Cache
- Redis: Spring Data Redis (Lettuce)
- 序列化: Jackson
