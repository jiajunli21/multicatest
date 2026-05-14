# 用户积分系统 — 架构设计文档

> 产出阶段：BEW-3（架构与数据编排）
> 生成时间：2026-05-14
> 上游输入：BEW-2（`.multica/plan.md`、`docs/plan.md`）

## 1. 模块划分

```
┌─────────────────────────────────────────────┐
│                  API Layer                   │
│  PointController  —  HTTP 路由、参数校验      │
│  请求/响应序列化、错误码映射                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│               Service Layer                  │
│  PointService       — 积分获取/消费           │
│  FreezeService      — 冻结/解冻/扣减          │
│  PointQueryService  — 余额查询/明细查询        │
│                                               │
│  职责：业务编排、幂等判断、事务边界控制、        │
│        乐观锁重试、FIFO 扣减策略               │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│             Repository Layer                 │
│  PointAccountRepo     — 账户 CRUD + 乐观锁    │
│  PointTransactionRepo — 明细写入 + 分页查询    │
│  FreezeRecordRepo     — 冻结记录管理           │
│                                               │
│  职责：纯数据访问，不含业务逻辑                  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              Database (SQL)                  │
│  point_accounts / point_transactions         │
│  freeze_records                              │
└─────────────────────────────────────────────┘
```

### 模块职责边界

| 模块 | 负责 | 不负责 |
|------|------|--------|
| PointController | 参数校验、路由、序列化 | 业务逻辑、事务管理 |
| PointService | 积分获取/消费编排、余额校验、FIFO 扣减、幂等 | 直接 SQL、HTTP 协议 |
| FreezeService | 冻结/解冻/扣减状态机、冻结余额校验 | 账户直接操作 |
| PointQueryService | 只读查询、分页、筛选 | 任何写操作 |
| Repository | SQL 执行、乐观锁版本匹配 | 业务规则判断 |

## 2. 核心数据流

### 2.1 积分获取

```
Client → Controller(校验参数)
       → PointService.earn()
           → Repository.findAccount(user_id) | 不存在 → lazy create
           → Repository.insertTransaction()  | 幂等键检查，重复则直接返回已有结果
           → Repository.updateAccountBalance(available += amount, total_earned += amount)
              | 乐观锁 version 匹配，冲突 → 重试（最多 3 次）
       → Controller → Response(account_snapshot)
```

### 2.2 积分消费

```
Client → Controller(校验参数)
       → PointService.spend()
           → Repository.findAccount(user_id)
           → 校验 available_balance >= amount（冻结余额不计入）
           → Repository.findEarliestExpiringEntries(user_id, amount)  | FIFO 队列
           → 逐条扣减明细的剩余可用额度
           → Repository.insertTransaction(type=SPEND)
           → Repository.updateAccountBalance(available -= amount, total_spent += amount)
              | 乐观锁，冲突 → 重试
       → Controller → Response(account_snapshot)
```

### 2.3 积分冻结

```
Client → Controller(校验参数)
       → FreezeService.freeze()
           → Repository.findAccount(user_id)
           → 校验 available_balance >= amount
           → Repository.updateAccountBalance(available -= amount, frozen += amount)
           → Repository.insertFreezeRecord()
           → Repository.insertTransaction(type=FREEZE)
           | 以上三步在同一数据库事务中
       → Controller → Response(freeze_record + account_snapshot)
```

### 2.4 积分解冻

```
Client → Controller(校验参数)
       → FreezeService.unfreeze()
           → Repository.findFreezeRecord(id)
           → 校验 freeze_record.status == ACTIVE && remaining >= amount
           → Repository.updateFreezeRecord(remaining -= amount)
           → Repository.updateAccountBalance(available += amount, frozen -= amount)
           → Repository.insertTransaction(type=UNFREEZE)
           | 同一事务
       → Controller → Response(freeze_record + account_snapshot)
```

### 2.5 冻结积分扣减

```
Client → Controller(校验参数)
       → FreezeService.deduct()
           → Repository.findFreezeRecord(id)
           → 校验 freeze_record.status == ACTIVE && remaining >= amount
           → Repository.updateFreezeRecord(remaining -= amount)
           → Repository.updateAccountBalance(frozen -= amount)
           → Repository.insertTransaction(type=DEDUCT)
           | 同一事务；注意：此操作不调整 available_balance
       → Controller → Response(freeze_record + account_snapshot)
```

## 3. 积分账户模型

### 3.1 账户生命周期

```
         首次 Earn
            │
    ┌───────▼────────┐
    │   不存在        │ ─── Lazy Create ───▶  正常活跃
    └────────────────┘                       │
                                      ┌──────▼──────┐
                                      │  可用余额 ≥ 0 │
                                      │  冻结余额 ≥ 0 │
                                      └──────────────┘
```

- 账户在用户首次积分获取时自动创建（Lazy Creation）
- 不存在"注销"或"删除"操作
- 账户通过 `user_id` 唯一标识，一对一关系

### 3.2 余额计算

```
total_balance = available_balance + frozen_balance
```

- `available_balance`：可消费余额，冻结操作从可用余额转入冻结余额
- `frozen_balance`：冻结余额，不可消费但仍在账户内
- `total_earned`：累计获取总额（只增不减，不可变累计值）
- `total_spent`：累计消费总额（只增不减，不可变累计值）

### 3.3 并发控制

采用**乐观锁（Optimistic Locking）**：

- `point_accounts` 表维护 `version` 字段（INT）
- 每次 UPDATE 时带上 `WHERE version = :expected_version`
- 同时 `SET version = version + 1`
- 若 affected_rows = 0，说明发生并发冲突，触发重试（最多 3 次）
- 重试时重新读取账户最新状态并重新执行业务校验

## 4. 积分明细模型

### 4.1 明细类型枚举

| 类型 | 含义 | 对可用余额 | 对冻结余额 |
|------|------|-----------|-----------|
| EARN | 积分获取 | +amount | 不变 |
| SPEND | 积分消费 | -amount | 不变 |
| FREEZE | 积分冻结 | -amount | +amount |
| UNFREEZE | 积分解冻 | +amount | -amount |
| DEDUCT | 冻结积分扣减 | 不变 | -amount |

### 4.2 幂等设计

联合唯一约束：`(user_id, type, reference_id)`

- `reference_id` 为外部业务单号（如订单号、活动 ID）
- 重复请求时返回已有记录，不重复变更余额
- 幂等命中返回 HTTP 200 + 原有结果（非 409）

### 4.3 过期时间

- 仅 `EARN` 类型设置 `expires_at`
- 消费时按 `expires_at ASC` 顺序优先扣减即将过期的积分
- 过期时间的实际过期判断由消费时的服务端时间对比完成
- 过期数据清理由外部定时任务负责，本系统提供查询接口支持（`WHERE expires_at < NOW() AND remaining > 0`）

## 5. 冻结/解冻语义

### 5.1 冻结记录状态机

```
         freeze()
            │
    ┌───────▼────────┐
    │     ACTIVE     │
    └───┬────────┬───┘
        │        │
  unfreeze()  deduct_frozen()
        │        │
   ┌────▼──┐  ┌──▼──────┐
   │RELEASED│  │DEDUCTED │
   └────────┘  └─────────┘
```

- ACTIVE → RELEASED：解冻，remaining 减少，余额转回可用
- ACTIVE → DEDUCTED：扣减，remaining 减少，余额直接销毁
- 不支持 RELEASED/DEDUCTED → ACTIVE 的回退
- 同一 FreezeRecord 可部分解冻/部分扣减（remaining 字段跟踪）

### 5.2 冻结与消费的关系

- 消费时只检查 `available_balance`，冻结余额对消费不可见
- 冻结中的积分无法被消费，必须先解冻
- 支持"冻结并扣减"的直接路径（如风控确认违规），不经过可用余额

## 6. 消费扣减逻辑

### 6.1 FIFO 扣减流程

```
1. 查询该用户所有 EARN 类型明细，筛选 remaining > 0 的记录
2. 按 expires_at ASC NULLS LAST 排序（NULL = 永不过期）
3. 逐条扣减：
   for each earn_record in sorted_list:
     if remaining_amount <= 0: break
     deduct = min(earn_record.remaining, remaining_amount)
     earn_record.remaining -= deduct
     remaining_amount -= deduct
4. 写入 SPEND 明细，记录本次消费总额
5. 更新账户 available_balance
```

### 6.2 扣减粒度

每条 EARN 明细维护 `remaining` 字段，表示该笔获取的积分中还剩余多少未被消费或被冻结：

- EARN 时：`remaining = amount`
- SPEND 时：按 FIFO 顺序递减对应 EARN 记录的 `remaining`
- FREEZE 时：冻结操作不追踪到具体 EARN 记录，仅从账户整体可用余额中扣除
- UNFREEZE 时：解冻后积分不关联到原 EARN 记录，作为通用可用余额

## 7. 并发与一致性风险

### 7.1 风险矩阵

| 场景 | 风险 | 缓解措施 |
|------|------|----------|
| 并发消费同一账户 | 余额超扣 | 乐观锁（version），冲突时重试 + 余额重校验 |
| 并发获取 + 消费 | 读取到过期余额 | 乐观锁覆盖账户 UPDATE，所有写操作竞争同一行锁 |
| 冻结 + 消费并发 | 冻结前余额被消费 | 乐观锁，冻结时校验 available >= amount（重试后可能不满足） |
| 解冻 + 扣减并发 | 冻结记录 remaining 超扣 | FreezeRecord 使用乐观锁或数据库行锁 |
| 重复业务单号 | 重复入账 | (user_id, type, reference_id) 联合唯一约束 |
| MySQL 行锁升级 | 死锁 | 统一资源访问顺序：先账户、后冻结记录；事务尽量短 |

### 7.2 事务边界

```
EARN/SPEND：
  单次事务范围 = INSERT point_transactions + UPDATE point_accounts
  若唯一约束冲突 → 返回已有记录（幂等），不开启写事务

FREEZE/UNFREEZE/DEDUCT：
  单次事务范围 = UPDATE freeze_records + UPDATE point_accounts + INSERT point_transactions
  三步在同一事务中，任何一步失败回滚全部
```

### 7.3 乐观锁重试策略

```
max_retries = 3
for attempt in 1..max_retries:
    account = repo.findByUserId(user_id)
    业务校验(account)
    affected = repo.updateWithVersion(account)
    if affected == 0: continue  // 版本冲突，重试
    return success
throw OptimisticLockException  // 3 次均失败
```

## 8. 查询接口结构建议

### 8.1 余额查询

```
GET /api/v1/points/balance?user_id={user_id}

Response:
{
  "user_id": "xxx",
  "available_balance": 10000,
  "frozen_balance": 500,
  "total_earned": 50000,
  "total_spent": 39500
}
```

查询策略：
- 单行查询，命中 `point_accounts.user_id` 唯一索引
- 若账户不存在，返回全 0（不创建账户，因为查询是只读操作）

### 8.2 明细查询

```
GET /api/v1/points/transactions?user_id={user_id}&type={type}&start={start}&end={end}&page={page}&size={size}

Response:
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20
}
```

查询策略：
- 使用 `(user_id, created_at DESC)` 联合索引，覆盖常规按时间倒序分页
- 可选 `type` 筛选在索引后过滤（或用 `(user_id, type, created_at)` 索引覆盖）
- 分页使用 OFFSET/LIMIT 或游标分页（created_at + id），避免深分页性能问题

### 8.3 冻结记录查询

```
GET /api/v1/points/freeze-records?user_id={user_id}&status={status}

Response:
{
  "items": [
    {
      "id": "xxx",
      "amount": 500,
      "remaining": 300,
      "reason": "风控冻结",
      "status": "ACTIVE",
      "created_at": "2026-05-14T08:00:00Z"
    }
  ]
}
```

## 9. 下游接口契约覆盖清单

供 BEW-4（接口契约）使用，以下对象和动作需要定义 API 契约：

### 9.1 对象

| 对象 | 关键字段 | 说明 |
|------|---------|------|
| PointAccount | user_id, available_balance, frozen_balance, total_earned, total_spent | 积分账户快照 |
| PointTransaction | id, user_id, type, amount, balance_after, frozen_after, source, reference_id, expires_at, created_at | 积分变动明细 |
| FreezeRecord | id, user_id, amount, remaining, reason, operator_id, status, created_at | 冻结记录 |
| PaginatedResult<T> | items, total, page, size | 分页容器 |
| ErrorResponse | code, message, detail | 错误响应 |

### 9.2 动作（API 端点）

| 方法 | 路径 | 请求体关键字段 | 响应 |
|------|------|---------------|------|
| POST | /api/v1/points/earn | user_id, amount, source, reference_id, expires_at? | PointAccount + PointTransaction |
| POST | /api/v1/points/spend | user_id, amount, reference_id | PointAccount + PointTransaction |
| POST | /api/v1/points/freeze | user_id, amount, reason, operator_id, reference_id | FreezeRecord + PointAccount + PointTransaction |
| POST | /api/v1/points/unfreeze | freeze_record_id, amount, operator_id, reference_id | FreezeRecord + PointAccount + PointTransaction |
| POST | /api/v1/points/deduct-frozen | freeze_record_id, amount, operator_id, reference_id | FreezeRecord + PointAccount + PointTransaction |
| GET | /api/v1/points/balance | user_id (query) | PointAccount |
| GET | /api/v1/points/transactions | user_id, type?, start?, end?, page, size (query) | PaginatedResult\<PointTransaction\> |
| GET | /api/v1/points/freeze-records | user_id, status? (query) | FreezeRecord[] |

### 9.3 错误码建议

| 错误码 | HTTP 状态 | 含义 |
|--------|----------|------|
| INSUFFICIENT_BALANCE | 422 | 可用余额不足 |
| INSUFFICIENT_FROZEN_BALANCE | 422 | 冻结余额不足 |
| ACCOUNT_NOT_FOUND | 404 | 账户不存在（仅写操作中可能出现） |
| FREEZE_RECORD_NOT_FOUND | 404 | 冻结记录不存在 |
| INVALID_FREEZE_STATUS | 422 | 冻结记录状态不允许当前操作 |
| DUPLICATE_REFERENCE | 200 | 幂等命中，返回已有结果 |
| INVALID_AMOUNT | 400 | 金额 ≤ 0 或超过单次上限 |
| VERSION_CONFLICT | 409 | 乐观锁冲突，重试耗尽 |
| INVALID_PARAMETER | 400 | 参数校验失败 |
