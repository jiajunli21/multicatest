# IA-006: 预警推送触发接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `POST` |
| 路径 | `/api/v1/morning-report/push/trigger` |
| 处理方式 | 新增 |
| 权限 | [default] 内部接口，暂默认有权限 |
| 类型 | 副作用接口 |

## 请求参数

无请求参数（内部触发，由数据计算完成后调用）。

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `status` | string | `"ok"`, `"error"`, `"no_subscribers"` | [verified] |
| `message` | string | 推送结果描述 | [verified] |
| `delivered_count` | integer | 成功送达数 | [default] |
| `failed_count` | integer | 推送失败数 | [default] |

### 权限兜底

[default] 内部接口，暂不做鉴权。
Phase 2 真实权限就绪后，仅允许内部服务调用。

### 空数据规则

无订阅用户时：
- `status` 返回 `"no_subscribers"`
- `delivered_count` 返回 `0`

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 推送服务不可用 | 500 | `PUSH_SERVICE_ERROR` | 记录日志，异步重试 |
| 部分用户推送失败 | 200 | — | status 返回 `"ok"`，failed_count > 0 |

### 推送消息体（内部构造）

```json
{
  "title": "[mock] 早盘宝每日关注",
  "etfs": [
    { "code": "510050", "name": "上证50ETF", "score": 0.89, "sector": "[mock] 大金融" },
    { "code": "510300", "name": "沪深300ETF", "score": 0.85, "sector": "[mock] 大金融" },
    { "code": "159915", "name": "创业板ETF", "score": 0.80, "sector": "[mock] 科技成长" },
    { "code": "512880", "name": "证券ETF", "score": 0.76, "sector": "[mock] 大金融" },
    { "code": "512100", "name": "中证1000ETF", "score": 0.71, "sector": "[mock] 中小盘" }
  ],
  "signal_date": "2026-05-25",
  "market_tag": "[default] 谨慎参与",
  "generated_at": "2026-05-25T09:30:00+08:00"
}
```

## 示例请求

```bash
curl -X POST "https://api.example.com/api/v1/morning-report/push/trigger"
```

## 示例响应

### 推送成功

```json
{
  "status": "ok",
  "message": "推送完成：成功 42，失败 0",
  "delivered_count": 42,
  "failed_count": 0
}
```

### 无订阅用户

```json
{
  "status": "no_subscribers",
  "message": "无订阅用户，未触发推送",
  "delivered_count": 0,
  "failed_count": 0
}
```

### 部分失败

```json
{
  "status": "ok",
  "message": "推送完成：成功 40，失败 2",
  "delivered_count": 40,
  "failed_count": 2
}
```

## 兼容性说明

- 新增接口，无兼容性问题
- Phase 2 替换为真实推送通道后，请求/响应结构不变
- 推送消息体中 ETF 字段为占位格式，真实推送按模板渲染
