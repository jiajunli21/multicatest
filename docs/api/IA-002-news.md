# IA-002: 资讯过滤接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `GET` |
| 路径 | `/api/v1/morning-report/news` |
| 处理方式 | 新增 |
| 权限 | [default] 无需登录 |
| Mock | 是 [mock] |

## Query 参数

| 参数名 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|--------|------|------|--------|------|------|
| `limit` | integer | 否 | 10 | 1-50 | 返回条数 |
| `offset` | integer | 否 | 0 | >= 0 | 偏移量（分页） |

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `news` | array | 资讯列表 | [mock] |
| `news[].title` | string | 资讯标题 | [mock] |
| `news[].summary` | string | 资讯摘要 | [mock] |
| `news[].time` | string | 发布时间 (ISO-8601) | [mock] |
| `news[].source` | string | 来源名称 | [mock] |
| `news[].url` | string | 资讯链接 | [mock] |
| `total` | integer | 符合条件的总数（用于分页） | [mock] |

### 权限兜底

无需登录，无权限校验。

### 空数据规则

无匹配资讯时：
- `news` 返回空数组 `[]`
- `total` 返回 `0`

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 参数校验失败 | 400 | `INVALID_PARAMS` | limit/offset 格式错误 |
| 资讯源不可用 | 200 | — | Phase 1 Mock 模式不受影响；Phase 2 降级返回缓存的资讯 |

## 示例请求

```bash
# 获取最新10条资讯
curl -X GET "https://api.example.com/api/v1/morning-report/news?limit=10&offset=0"

# 获取更多
curl -X GET "https://api.example.com/api/v1/morning-report/news?limit=20&offset=10"
```

## 示例响应

### 正常响应

```json
{
  "news": [
    {
      "title": "[mock] ETF市场周报：资金持续流入宽基ETF",
      "summary": "本周ETF市场整体呈现净流入态势，宽基ETF仍是资金主要配置方向...",
      "time": "2026-05-25T08:30:00Z",
      "source": "[mock] ETF资讯",
      "url": "https://example.com/news/1"
    },
    {
      "title": "[mock] 早盘关注：科技板块ETF表现活跃",
      "summary": "受隔夜美股科技股上涨带动，今日科技类ETF早盘表现活跃...",
      "time": "2026-05-25T08:00:00Z",
      "source": "[mock] 市场快讯",
      "url": "https://example.com/news/2"
    }
  ],
  "total": 5
}
```

### 空数据响应

```json
{
  "news": [],
  "total": 0
}
```

## 兼容性说明

- 新增接口，无兼容性问题
- Phase 2 替换为真实资讯接口后，字段结构不变
- 分页参数 `limit`/`offset` 为标准设计
