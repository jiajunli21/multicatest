# IA-003: 历史表现接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `GET` |
| 路径 | `/api/v1/morning-report/history` |
| 处理方式 | 新增 |
| 权限 | [default] 无需登录 |
| Mock | 否 [verified]（Phase 2 已桥接 DB 历史数据） |

## Query 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `date` | string (YYYY-MM-DD) | 否 | — | 指定日期，不传返回全部历史 |

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `history` | array | 历史记录列表，按 date 降序 | [verified] |
| `history[].date` | string | 推送日期 (YYYY-MM-DD) | [verified] |
| `history[].etfs` | array | 当日推送的 ETF 列表 | [verified] |
| `history[].etfs[].code` | string | ETF 代码 | [verified] |
| `history[].etfs[].name` | string | ETF 名称 | [verified] |
| `history[].etfs[].signal_3d_return` | string \| null | 信号后第3个交易日涨幅，不足3交易日为 null | [default] |
| `history[].etfs[].current_return` | string \| null | 当前累计涨幅（信号日至今） | [default] |

### 权限兜底

无需登录，无权限校验。

### 空数据规则

无历史数据时：
- `history` 返回空数组 `[]`

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 参数校验失败 | 400 | `INVALID_PARAMS` | date 格式错误 |
| 数据未落库 | 200 | — | 返回空数组 |
| 涨幅计算时为非交易日 | — | — | `current_return` 使用最近交易日计算 |

## 示例请求

```bash
# 获取全部历史
curl -X GET "https://api.example.com/api/v1/morning-report/history"

# 指定日期
curl -X GET "https://api.example.com/api/v1/morning-report/history?date=2026-05-22"
```

## 示例响应

### 正常响应

```json
{
  "history": [
    {
      "date": "2026-05-22",
      "etfs": [
        { "code": "510050", "name": "上证50ETF", "signal_3d_return": "+0.85%", "current_return": "+1.23%" },
        { "code": "159915", "name": "创业板ETF", "signal_3d_return": "+1.52%", "current_return": "+2.10%" },
        { "code": "510300", "name": "沪深300ETF", "signal_3d_return": "+0.63%", "current_return": "+0.98%" },
        { "code": "512880", "name": "证券ETF", "signal_3d_return": "-0.21%", "current_return": "+0.15%" },
        { "code": "588000", "name": "科创50ETF", "signal_3d_return": "+2.34%", "current_return": "+3.01%" }
      ]
    }
  ]
}
```

### 不足3交易日（signal_3d_return 为 null）

```json
{
  "history": [
    {
      "date": "2026-05-25",
      "etfs": [
        { "code": "588000", "name": "科创50ETF", "signal_3d_return": null, "current_return": "+0.52%" }
      ]
    }
  ]
}
```

### 空数据响应

```json
{
  "history": []
}
```

## 兼容性说明

- 新增接口，无兼容性问题
- `signal_3d_return` 和 `current_return` 格式为带符号的百分比字符串（如 `"+0.85%"`），前端可直接展示
- Phase 2 桥接真实历史数据后，字段结构不变
