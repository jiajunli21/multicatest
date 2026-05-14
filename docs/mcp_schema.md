# MCP Tool Schema — 用户积分系统

## 概述

基于 Model Context Protocol (MCP) 规范，定义用户积分系统的 7 个工具（Tool）。每个工具对应一个 API 端点，供 AI Agent 通过 MCP Server 调用积分系统。

**上游依赖**: `docs/architecture.md` + `prisma/schema.prisma`

---

## 工具清单

| 工具名称 | 对应 API | 说明 |
|---------|---------|------|
| `earn_points` | POST /points/earn | 为用户增加积分，账户不存在时自动创建 |
| `spend_points` | POST /points/spend | 扣减用户积分，行锁保证并发安全 |
| `freeze_points` | POST /points/freeze | 冻结用户积分，需设置超时时间 |
| `unfreeze_points` | POST /points/unfreeze | 解冻已冻结积分，恢复可用余额 |
| `frozen_deduct_points` | POST /points/frozen-deduct | 从冻结积分直接扣减（支付完成场景） |
| `list_transactions` | GET /points/transactions | 分页查询积分流水明细 |
| `get_balance` | GET /points/balance | 查询用户积分余额及统计 |

---

## 工具详细定义

### 1. earn_points — 积分获取

**描述**: 为用户增加积分。使用原子 UPDATE 操作保证并发安全（无需行锁）。账户不存在时自动创建。通过 `idempotent_key` 保证幂等性。

**输入 Schema** (JSON Schema):

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "maxLength": 64,
      "description": "用户标识"
    },
    "amount": {
      "type": "integer",
      "minimum": 1,
      "description": "获取积分数量，必须大于 0"
    },
    "idempotent_key": {
      "type": "string",
      "maxLength": 128,
      "description": "幂等键，建议格式: earn:{user_id}:{uuid_v4}。重复请求返回相同结果。"
    },
    "remark": {
      "type": "string",
      "maxLength": 256,
      "description": "备注（可选）"
    }
  },
  "required": ["user_id", "amount", "idempotent_key"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string", "enum": ["SUCCESS"] },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "transaction_id": { "type": "integer", "description": "流水记录 ID" },
        "balance_before": { "type": "integer" },
        "balance_after": { "type": "integer" }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_IDEMPOTENT_CONFLICT` | 409 | 重复幂等键，应返回首次结果 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

### 2. spend_points — 积分消费

**描述**: 扣减用户可用积分。使用 `SELECT FOR UPDATE` 行锁 + 乐观锁版本号保证并发安全，防止超卖。扣减前校验余额是否充足。

**输入 Schema**:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "maxLength": 64,
      "description": "用户标识"
    },
    "amount": {
      "type": "integer",
      "minimum": 1,
      "description": "消费积分数量，必须大于 0"
    },
    "idempotent_key": {
      "type": "string",
      "maxLength": 128,
      "description": "幂等键，建议格式: spend:{user_id}:{uuid_v4}"
    },
    "remark": {
      "type": "string",
      "maxLength": 256,
      "description": "备注（可选）"
    }
  },
  "required": ["user_id", "amount", "idempotent_key"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "transaction_id": { "type": "integer" },
        "balance_before": { "type": "integer" },
        "balance_after": { "type": "integer" }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_ACCOUNT_NOT_FOUND` | 404 | 积分账户不存在 |
| `POINTS_INSUFFICIENT_BALANCE` | 422 | 可用积分余额不足 |
| `POINTS_IDEMPOTENT_CONFLICT` | 409 | 重复幂等键 |
| `POINTS_VERSION_CONFLICT` | 409 | 乐观锁版本冲突，客户端应重试 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

### 3. freeze_points — 积分冻结

**描述**: 冻结用户指定数量的积分，从可用余额转入冻结余额。需设置超时时间，超时后由定时任务（每 30 秒扫描）自动释放。冻结期间积分不可消费。

**输入 Schema**:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "maxLength": 64,
      "description": "用户标识"
    },
    "amount": {
      "type": "integer",
      "minimum": 1,
      "description": "冻结积分数量"
    },
    "idempotent_key": {
      "type": "string",
      "maxLength": 128,
      "description": "幂等键，建议格式: freeze:{user_id}:{uuid_v4}"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "冻结超时时间（ISO 8601），超时后定时任务自动解冻"
    },
    "remark": {
      "type": "string",
      "maxLength": 256,
      "description": "冻结原因（可选）"
    }
  },
  "required": ["user_id", "amount", "idempotent_key", "expires_at"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "freeze_id": { "type": "integer", "description": "冻结记录 ID" },
        "balance": { "type": "integer", "description": "冻结后可用余额" },
        "frozen_balance": { "type": "integer", "description": "冻结后冻结余额" },
        "expires_at": { "type": "string", "format": "date-time", "description": "冻结超时时间" }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_ACCOUNT_NOT_FOUND` | 404 | 积分账户不存在 |
| `POINTS_INSUFFICIENT_BALANCE` | 422 | 可用积分余额不足 |
| `POINTS_IDEMPOTENT_CONFLICT` | 409 | 重复幂等键 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

### 4. unfreeze_points — 冻结解冻

**描述**: 解冻之前冻结的积分，将冻结余额转回可用余额。需校验冻结记录状态为 `active` 且未超时。

**输入 Schema**:

```json
{
  "type": "object",
  "properties": {
    "freeze_id": {
      "type": "integer",
      "description": "冻结记录 ID"
    },
    "idempotent_key": {
      "type": "string",
      "maxLength": 128,
      "description": "幂等键，建议格式: unfreeze:{user_id}:{uuid_v4}"
    }
  },
  "required": ["freeze_id", "idempotent_key"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "freeze_id": { "type": "integer" },
        "status": { "type": "string", "enum": ["released"] },
        "balance": { "type": "integer", "description": "解冻后可用余额" },
        "frozen_balance": { "type": "integer", "description": "解冻后冻结余额" }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_FREEZE_NOT_FOUND` | 404 | 冻结记录不存在 |
| `POINTS_FREEZE_STATUS_INVALID` | 422 | 冻结状态不匹配（已 released 或 deducted） |
| `POINTS_FREEZE_EXPIRED` | 422 | 冻结已超时 |
| `POINTS_IDEMPOTENT_CONFLICT` | 409 | 重复幂等键 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

### 5. frozen_deduct_points — 冻结扣减

**描述**: 从已冻结积分中直接扣减（不退回可用余额），用于订单支付完成等场景。被扣减的冻结金额从 `frozen_balance` 中扣除，冻结记录状态变为 `deducted`。

**输入 Schema**:

```json
{
  "type": "object",
  "properties": {
    "freeze_id": {
      "type": "integer",
      "description": "冻结记录 ID"
    },
    "idempotent_key": {
      "type": "string",
      "maxLength": 128,
      "description": "幂等键，建议格式: frozen_deduct:{user_id}:{uuid_v4}"
    }
  },
  "required": ["freeze_id", "idempotent_key"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "freeze_id": { "type": "integer" },
        "status": { "type": "string", "enum": ["deducted"] },
        "frozen_balance": { "type": "integer", "description": "扣减后冻结余额" }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_FREEZE_NOT_FOUND` | 404 | 冻结记录不存在 |
| `POINTS_FREEZE_STATUS_INVALID` | 422 | 冻结状态不匹配 |
| `POINTS_FREEZE_EXPIRED` | 422 | 冻结已超时 |
| `POINTS_IDEMPOTENT_CONFLICT` | 409 | 重复幂等键 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

### 6. list_transactions — 积分明细查询

**描述**: 分页查询用户积分流水明细，按 `created_at` 降序排列。支持按交易类型和时间范围筛选。

**输入 Schema**:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "maxLength": 64,
      "description": "用户标识"
    },
    "type": {
      "type": "string",
      "enum": ["earn", "spend", "freeze", "unfreeze", "frozen_deduct"],
      "description": "交易类型筛选（可选）"
    },
    "start_time": {
      "type": "string",
      "format": "date-time",
      "description": "起始时间 ISO 8601（可选）"
    },
    "end_time": {
      "type": "string",
      "format": "date-time",
      "description": "结束时间 ISO 8601（可选）"
    },
    "page": {
      "type": "integer",
      "default": 1,
      "minimum": 1,
      "description": "页码，从 1 开始"
    },
    "page_size": {
      "type": "integer",
      "default": 20,
      "minimum": 1,
      "maximum": 100,
      "description": "每页数量，上限 100"
    }
  },
  "required": ["user_id"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "total": { "type": "integer", "description": "总记录数" },
        "page": { "type": "integer" },
        "page_size": { "type": "integer" },
        "items": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "id": { "type": "integer", "description": "流水 ID" },
              "user_id": { "type": "string" },
              "type": { "type": "string", "enum": ["earn", "spend", "freeze", "unfreeze", "frozen_deduct"] },
              "amount": { "type": "integer" },
              "balance_before": { "type": "integer" },
              "balance_after": { "type": "integer" },
              "freeze_id": { "type": "integer", "description": "关联冻结记录 ID（冻结/解冻/扣减类型时有值）" },
              "remark": { "type": "string" },
              "created_at": { "type": "string", "format": "date-time" }
            }
          }
        }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_ACCOUNT_NOT_FOUND` | 404 | 积分账户不存在 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

### 7. get_balance — 积分余额查询

**描述**: 查询用户当前积分余额、冻结余额及累计统计数据。包含乐观锁版本号，供后续操作做并发校验。

**输入 Schema**:

```json
{
  "type": "object",
  "properties": {
    "user_id": {
      "type": "string",
      "maxLength": 64,
      "description": "用户标识"
    }
  },
  "required": ["user_id"]
}
```

**输出 Schema**:

```json
{
  "type": "object",
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "data": {
      "type": "object",
      "properties": {
        "user_id": { "type": "string" },
        "balance": { "type": "integer", "description": "可用积分余额" },
        "frozen_balance": { "type": "integer", "description": "冻结积分余额" },
        "total_earned": { "type": "integer", "description": "累计获取积分" },
        "total_spent": { "type": "integer", "description": "累计消费积分" },
        "version": { "type": "integer", "description": "乐观锁版本号，后续写操作需要" }
      }
    }
  }
}
```

**错误码**:

| 错误码 | HTTP | 说明 |
|--------|------|------|
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 |
| `POINTS_ACCOUNT_NOT_FOUND` | 404 | 积分账户不存在 |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 |

---

## 完整错误码映射表

| 错误码 | HTTP 状态码 | 说明 | 触发条件 | 适用工具 |
|--------|-----------|------|---------|---------|
| `SUCCESS` | 200 | 操作成功 | — | 全部 |
| `POINTS_INVALID_PARAM` | 400 | 参数校验失败 | amount ≤ 0、user_id 为空、必填字段缺失 | 全部 |
| `POINTS_ACCOUNT_NOT_FOUND` | 404 | 积分账户不存在 | 查询或操作未初始化的用户账户 | spend, freeze, list, balance |
| `POINTS_INSUFFICIENT_BALANCE` | 422 | 可用积分余额不足 | balance < amount | spend, freeze |
| `POINTS_FREEZE_NOT_FOUND` | 404 | 冻结记录不存在 | freeze_id 不存在 | unfreeze, frozen_deduct |
| `POINTS_FREEZE_STATUS_INVALID` | 422 | 冻结状态不匹配 | freeze.status ≠ 'active' | unfreeze, frozen_deduct |
| `POINTS_FREEZE_EXPIRED` | 422 | 冻结已超时 | expires_at < NOW() | unfreeze, frozen_deduct |
| `POINTS_IDEMPOTENT_CONFLICT` | 409 | 重复幂等键 | idempotent_key 已存在 | earn, spend, freeze, unfreeze, frozen_deduct |
| `POINTS_VERSION_CONFLICT` | 409 | 乐观锁版本冲突 | version 不匹配 | spend |
| `POINTS_INTERNAL_ERROR` | 500 | 系统内部错误 | 数据库异常、未知运行时错误 | 全部 |

---

## 流水类型枚举

| 值 | 类型 | 说明 | 余额变化 |
|----|------|------|---------|
| `earn` | 积分获取 | 签到、任务、活动、管理员调整 | balance ↑ |
| `spend` | 积分消费 | 兑换、抵扣 | balance ↓ |
| `freeze` | 积分冻结 | 订单支付中、争议处理 | balance ↓, frozen_balance ↑ |
| `unfreeze` | 积分解冻 | 订单取消、争议解决 | balance ↑, frozen_balance ↓ |
| `frozen_deduct` | 冻结扣减 | 订单支付完成 | frozen_balance ↓ |

---

## 冻结状态枚举

| 值 | 说明 | 可转换到 |
|----|------|---------|
| `active` | 冻结中 | `released`（解冻）, `deducted`（扣减） |
| `released` | 已解冻 | —（终态） |
| `deducted` | 已扣减 | —（终态） |

---

## 幂等键设计建议

| 操作 | 建议格式 |
|------|---------|
| earn | `earn:{user_id}:{uuid_v4}` |
| spend | `spend:{user_id}:{uuid_v4}` |
| freeze | `freeze:{user_id}:{uuid_v4}` |
| unfreeze | `unfreeze:{user_id}:{uuid_v4}` |
| frozen_deduct | `frozen_deduct:{user_id}:{uuid_v4}` |

幂等键由客户端生成，服务端通过 `UNIQUE(idempotent_key)` 约束保证全局唯一。重复请求返回首次结果而非报错。

---

## 并发控制说明

| 操作 | 并发策略 | 说明 |
|------|---------|------|
| earn | 原子 UPDATE (无锁) | `UPDATE ... SET balance = balance + $1` 无超卖风险 |
| spend | SELECT FOR UPDATE + 版本号 | 行锁串行化 + 乐观锁双重校验 |
| freeze | SELECT FOR UPDATE + 版本号 | 同上 |
| unfreeze | SELECT FOR UPDATE | 行锁保证释放原子性，防定时任务竞态 |
| frozen_deduct | SELECT FOR UPDATE | 同上 |
| list / balance | 普通 SELECT (无锁) | 只读操作，无需加锁 |
