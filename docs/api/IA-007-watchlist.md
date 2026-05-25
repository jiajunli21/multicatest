# IA-007: 一键加自选接口

## 接口概览

| 属性 | 值 |
|------|-----|
| 方法 | `POST` |
| 路径 | `/api/v1/morning-report/watchlist/add` |
| 处理方式 | 新增 |
| 权限 | [default] 暂默认有权限 |
| 幂等 | 是 |
| 类型 | 副作用接口 |

## Body 参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `user_id` | string | 是 | — | 用户标识 |
| `date` | string (YYYY-MM-DD) | 否 | 当日 | 指定早盘宝日期，用于分组命名 |

## 返回数据

### 字段说明

| 字段路径 | 类型 | 说明 | 状态 |
|-----------|------|------|------|
| `status` | string | `"ok"`, `"partial"`, `"error"` | [verified] |
| `added_count` | integer | 成功添加到自选的 ETF 数量 | [default] |
| `failed_list` | array | 添加失败的 ETF 列表 | — |
| `failed_list[].code` | string | 失败的 ETF 代码 | — |
| `failed_list[].reason` | string | 失败原因 | — |

### 权限兜底

[default] 暂默认有权限，不做用户身份校验。
Phase 2 真实权限就绪后，无权限返回 403。

### 错误/降级规则

| 场景 | HTTP 状态码 | code | 说明 |
|------|-------------|------|------|
| 参数校验失败 | 400 | `INVALID_PARAMS` | user_id 为空或 date 格式错误 |
| 部分 ETF 添加失败 | 200 | — | status=`"partial"`，在 failed_list 中说明原因 |
| 全部失败 | 200 | — | status=`"error"`，added_count=0 |
| 无权限（Phase 2） | 403 | `FORBIDDEN` | [pending] |

### 幂等规则

- 自选分组名为 `"{date}_早盘宝"`（如 `"2026-05-25_早盘宝"`）
- 同一 ETF 重复添加到同一分组：返回 ok，不计入 `added_count`
- 分组已存在的 ETF 已添加时：跳过，不计入 `added_count`

## 示例请求

```bash
# 添加到当日早盘宝分组
curl -X POST "https://api.example.com/api/v1/morning-report/watchlist/add" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_12345"}'

# 指定日期
curl -X POST "https://api.example.com/api/v1/morning-report/watchlist/add" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_12345", "date": "2026-05-22"}'
```

## 示例响应

### 全部成功

```json
{
  "status": "ok",
  "added_count": 5,
  "failed_list": []
}
```

### 部分失败

```json
{
  "status": "partial",
  "added_count": 4,
  "failed_list": [
    { "code": "512100", "reason": "[mock] 自选分组已满" }
  ]
}
```

## 兼容性说明

- 新增接口，无兼容性问题
- Phase 1 仅验证结构+幂等设计，Phase 2 桥接真实自选接口
- 分组命名规则 `{date}_早盘宝` 确认后可调整
