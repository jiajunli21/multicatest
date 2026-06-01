# ETF Tab 板块统计 C 端业务接口契约

## 接口概览

| 项目 | 内容 |
|---|---|
| **接口名称** | 板块统计 ETF tab 数据查询 |
| **方法** | GET |
| **路径** | `/api/v1/etf/plate-stat/rank` |
| **处理方式** | 新增（ifund-hq-project） |
| **数据来源** | Redis key `plateStatEtf:rank:data` → 数据开发 Agent 定时写入 |

## 请求参数

无请求参数。全量返回 8 份榜单数据（4 维度 × 前9/后9）。

## 响应结构

### Response Envelope

```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "timestamp": 1717200000
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码：0=成功，-1=错误 |
| message | string | 状态消息 |
| data | object | 榜单数据（RankData） |
| timestamp | int | 响应时间戳（Unix timestamp） |

### RankData

| 字段 | 类型 | 说明 |
|---|---|---|
| updateTime | int? | 数据更新时间（Unix timestamp） |
| changeRatioTop9 | EtfRankItem[] | 涨幅前9 |
| changeRatioBottom9 | EtfRankItem[] | 涨幅后9 |
| speedRatioTop9 | EtfRankItem[] | 涨速前9 |
| speedRatioBottom9 | EtfRankItem[] | 涨速后9 |
| volumeRatioTop9 | EtfRankItem[] | 量比前9 |
| volumeRatioBottom9 | EtfRankItem[] | 量比后9 |
| limitUpCountTop9 | EtfRankItem[] | 涨停数前9 |
| limitUpCountBottom9 | EtfRankItem[] | 涨停数后9 |

### EtfRankItem

| 字段 | 类型 | 说明 |
|---|---|---|
| code | string | ETF代码 |
| name | string | ETF名称 |
| chgpct | number? | 涨跌幅(%) |
| speedRatio | number? | 涨速 |
| volumeRatio | number? | 量比 |
| etfLimitUpStockCnt | int? | 涨停个股数 |
| topLeadStockCode | string? | 领涨成分股代码 |
| topLeadStockName | string? | 领涨成分股名称 |
| topLeadStockChangeRatio | number? | 领涨成分股涨跌幅(%) |
| bottomLeadStockCode | string? | 领跌成分股代码 |
| bottomLeadStockName | string? | 领跌成分股名称 |
| bottomLeadStockChangeRatio | number? | 领跌成分股涨跌幅(%) |

## 错误态与空态

| 场景 | code | message | data |
|---|---|---|---|
| 正常返回 | 0 | "success" | 榜单数据 |
| Redis key 不存在（首次运行前） | 0 | "success" | 8 份空数组 |
| Redis 连接失败 | 0 | "success" | 8 份空数组（降级） |
| 数据解析异常 | 0 | "success" | 8 份空数组（降级） |

## 缓存策略

```
请求 → Caffeine 本地缓存（TTL 30s）
  ├─ 命中 → 直接返回
  └─ 未命中 → Redis.get("plateStatEtf:rank:data")
       ├─ 命中 → 回填 Caffeine → 返回
       └─ 未命中/异常 → 返回空榜单结构
```

## 示例请求

```bash
curl -X GET http://localhost:8000/api/v1/etf/plate-stat/rank
```

## 示例响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "updateTime": 1717200000,
    "changeRatioTop9": [
      {
        "code": "512880",
        "name": "证券ETF",
        "chgpct": 2.35,
        "speedRatio": 0.0,
        "volumeRatio": 1.0,
        "etfLimitUpStockCnt": 3,
        "topLeadStockCode": "600030",
        "topLeadStockName": "中信证券",
        "topLeadStockChangeRatio": 5.2,
        "bottomLeadStockCode": "000776",
        "bottomLeadStockName": "广发证券",
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
  },
  "timestamp": 1717200000
}
```

## 空数据示例响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "updateTime": null,
    "changeRatioTop9": [],
    "changeRatioBottom9": [],
    "speedRatioTop9": [],
    "speedRatioBottom9": [],
    "volumeRatioTop9": [],
    "volumeRatioBottom9": [],
    "limitUpCountTop9": [],
    "limitUpCountBottom9": []
  },
  "timestamp": 1717200000
}
```

## 权限

本阶段无权限层（软阻塞假设：ETF tab 无需单独权限控制）。

## 生产技术栈

| 项目 | 说明 |
|---|---|
| 运行时 | Python 3.12+ |
| 框架 | FastAPI |
| 缓存 | cachetools.TTLCache（Caffeine 等价，TTL 30s） |
| Redis | redis-py |
| 交付类型 | 流程验证版 scaffold |
| 生产就绪 | 否（真实生产需迁移至 Java） |

## 兼容性

- 新增接口，无向后兼容风险
- speedRatio/volumeRatio 维度榜单的 Mock 数据原样透传
- 领涨成分股空字符串/null 原样透传
- 不影响原有板块统计 tab 接口
