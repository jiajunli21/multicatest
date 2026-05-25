# IA-005: 预警订阅接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `POST` |
| 路径 | `/api/v1/morning-report/subscribe` |
| 处理方式 | 新增 |
| 权限 | [default] 暂默认有权限 |
| 幂等 | 是 |

## Body 参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `action` | string | 是 | `"subscribe"` 或 `"unsubscribe"` |
| `user_id` | string | 是 | 用户标识 |

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `status` | string | `"ok"` 或 `"error"` | [verified] |
| `message` | string | 操作结果描述 | [verified] |

### 权限兜底

[default] 暂默认有权限，不做用户身份校验。
Phase 2 真实权限就绪后，无权限返回 403。

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 参数校验失败 | 400 | `INVALID_PARAMS` | action 或 user_id 不合法 |
| 存储写入失败 | 500 | `INTERNAL_ERROR` | 订阅状态持久化失败 |
| 无权限（Phase 2） | 403 | `FORBIDDEN` | [pending] 真实权限校验后启用 |

### 幂等规则

- 重复 `subscribe`：返回 `{ "status": "ok", "message": "订阅成功" }`，不重复写入
- 重复 `unsubscribe`：返回 `{ "status": "ok", "message": "已取消订阅" }`，不报错

## 示例请求

```bash
# 订阅
curl -X POST "https://api.example.com/api/v1/morning-report/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"action": "subscribe", "user_id": "user_12345"}'

# 取消订阅
curl -X POST "https://api.example.com/api/v1/morning-report/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"action": "unsubscribe", "user_id": "user_12345"}'
```

## 示例响应

### 订阅成功

```json
{
  "status": "ok",
  "message": "订阅成功"
}
```

### 取消订阅成功

```json
{
  "status": "ok",
  "message": "已取消订阅"
}
```

### 参数错误

```json
{
  "error": "参数校验失败",
  "code": "INVALID_PARAMS",
  "detail": "[{\"msg\":\"action 必须为 subscribe 或 unsubscribe\"}]"
}
```

## 兼容性说明

- 新增接口，无兼容性问题
- Phase 2 增加权限校验后，合法用户行为不变
- 幂等设计确保前后端重试安全
