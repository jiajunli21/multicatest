# IA-001: 早盘宝首页数据接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `GET` |
| 路径 | `/api/v1/morning-report/home` |
| 处理方式 | 新增 |
| 权限 | [default] 无需登录 |
| Mock | 赛道、标签 [mock]；ETF分数、排名 [verified] (SQLite DB) |

## Query 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `date` | string (YYYY-MM-DD) | 否 | 最新 | 指定交易日，不传默认返回最新数据 |

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `top5_etfs` | array | Top5 ETF 列表，按 score 降序 | — |
| `top5_etfs[].code` | string | ETF 代码 | [verified] |
| `top5_etfs[].name` | string | ETF 名称 | [verified] |
| `top5_etfs[].score` | number | ETF 综合分数 (2位小数) | [verified] |
| `top5_etfs[].rank` | integer | 排名 (1-5) | [verified] |
| `top5_etfs[].sector` | string | 三级赛道名称 | [mock] |
| `top5_etfs[].tags` | string[] | 个基标签列表 | [mock] |
| `sectors` | array | 赛道分布 | — |
| `sectors[].name` | string | 赛道名称 | [mock] |
| `sectors[].etfs` | array | 该赛道下的 ETF 列表 | — |
| `signal_date` | string | 信号日 (YYYY-MM-DD) | [default] |
| `market_tag` | string | 市场标签：`"谨慎参与"` 或 `"积极参与"` | [default] |
| `update_time` | string | 数据更新时间 (ISO-8601) | [verified] |

### 权限兜底

无需登录，无权限校验。

### 空数据规则

当数据未就绪或无符合条件的 ETF 时：
- `top5_etfs` 返回空数组 `[]`
- `sectors` 返回空数组 `[]`
- `market_tag` 返回 `"数据未就绪"`
- 仍返回 `update_time`

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 评分计算未完成 | 200 | — | 返回空列表 + 特定 signal_date 说明 |
| 外部行情数据不可用 | 200 | — | 降级：使用最近一次有效计算缓存 |
| 服务异常 | 500 | `INTERNAL_ERROR` | — |

## 示例请求

```bash
# 获取最新早盘宝首页数据
curl -X GET "https://api.example.com/api/v1/morning-report/home"

# 指定日期
curl -X GET "https://api.example.com/api/v1/morning-report/home?date=2026-05-25"
```

## 示例响应

### 正常响应

```json
{
  "top5_etfs": [
    {
      "code": "510050",
      "name": "上证50ETF",
      "score": 0.89,
      "rank": 1,
      "sector": "[mock] 大金融",
      "tags": ["[mock] 资金流入", "[mock] 低估值"]
    },
    {
      "code": "510300",
      "name": "沪深300ETF",
      "score": 0.85,
      "rank": 2,
      "sector": "[mock] 大金融",
      "tags": ["[mock] 外资增持", "[mock] 低波动"]
    },
    {
      "code": "159915",
      "name": "创业板ETF",
      "score": 0.80,
      "rank": 3,
      "sector": "[mock] 科技成长",
      "tags": ["[mock] 超跌反弹", "[mock] 高弹性"]
    },
    {
      "code": "512880",
      "name": "证券ETF",
      "score": 0.76,
      "rank": 4,
      "sector": "[mock] 大金融",
      "tags": ["[mock] 券商异动"]
    },
    {
      "code": "512100",
      "name": "中证1000ETF",
      "score": 0.71,
      "rank": 5,
      "sector": "[mock] 中小盘",
      "tags": ["[mock] 小盘活跃", "[mock] 资金关注"]
    }
  ],
  "sectors": [
    {
      "name": "[mock] 大金融",
      "etfs": [
        { "code": "510050", "name": "上证50ETF", "score": 0.89, "rank": 1, "sector": "[mock] 大金融", "tags": ["[mock] 资金流入", "[mock] 低估值"] },
        { "code": "510300", "name": "沪深300ETF", "score": 0.85, "rank": 2, "sector": "[mock] 大金融", "tags": ["[mock] 外资增持", "[mock] 低波动"] },
        { "code": "512880", "name": "证券ETF", "score": 0.76, "rank": 4, "sector": "[mock] 大金融", "tags": ["[mock] 券商异动"] }
      ]
    },
    {
      "name": "[mock] 科技成长",
      "etfs": [
        { "code": "159915", "name": "创业板ETF", "score": 0.80, "rank": 3, "sector": "[mock] 科技成长", "tags": ["[mock] 超跌反弹", "[mock] 高弹性"] }
      ]
    },
    {
      "name": "[mock] 中小盘",
      "etfs": [
        { "code": "512100", "name": "中证1000ETF", "score": 0.71, "rank": 5, "sector": "[mock] 中小盘", "tags": ["[mock] 小盘活跃", "[mock] 资金关注"] }
      ]
    }
  ],
  "signal_date": "2026-05-25",
  "market_tag": "[default] 谨慎参与",
  "update_time": "2026-05-25T09:30:00+08:00"
}
```

### 空数据响应

```json
{
  "top5_etfs": [],
  "sectors": [],
  "signal_date": "2026-05-25",
  "market_tag": "[default] 数据未就绪",
  "update_time": "2026-05-25T09:00:00+08:00"
}
```

## 兼容性说明

- 新增接口，无兼容性问题
- Phase 2 赛道和标签字段将从 [mock] 切换为真实数据
- 字段结构保持稳定，不计划破坏性变更
