# 用户积分系统 — 架构设计文档

## 1. 总体架构

```
┌─────────────────────────────────────────────────┐
│                   API Layer                      │
│  积分获取 │ 积分消费 │ 冻结/解冻 │ 明细查询      │
├─────────────────────────────────────────────────┤
│                 Service Layer                    │
│  幂等校验 → 余额校验 → 行锁扣减 → 流水记录       │
├─────────────────────────────────────────────────┤
│                Repository Layer                  │
│  AccountRepo │ TransactionRepo │ FreezeRepo      │
├─────────────────────────────────────────────────┤
│              PostgreSQL (主库)                    │
│  accounts │ transactions │ freezes               │
└─────────────────────────────────────────────────┘
```

## 2. 数据模型

### 2.1 accounts（积分账户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PK | 主键 |
| user_id | VARCHAR(64) | NOT NULL, UNIQUE | 用户标识 |
| balance | BIGINT | NOT NULL, DEFAULT 0, CHECK (>= 0) | 当前可用余额，不允许负数 |
| frozen_balance | BIGINT | NOT NULL, DEFAULT 0, CHECK (>= 0) | 已冻结金额 |
| total_earned | BIGINT | NOT NULL, DEFAULT 0 | 历史累计获取 |
| total_spent | BIGINT | NOT NULL, DEFAULT 0 | 历史累计消费 |
| version | INTEGER | NOT NULL, DEFAULT 0 | 乐观锁版本号 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

**约束:** `balance + frozen_balance <= total_earned`（业务层校验）

### 2.2 transactions（积分流水表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PK | 主键 |
| idempotent_key | VARCHAR(128) | NOT NULL, UNIQUE | 幂等键（客户端生成，全局唯一） |
| user_id | VARCHAR(64) | NOT NULL, INDEX | 用户标识 |
| type | VARCHAR(16) | NOT NULL | 类型: earn / spend / freeze / unfreeze / frozen_deduct |
| amount | BIGINT | NOT NULL, CHECK (> 0) | 变动金额 |
| balance_before | BIGINT | NOT NULL | 变动前余额 |
| balance_after | BIGINT | NOT NULL | 变动后余额 |
| freeze_id | BIGINT | nullable, FK → freezes.id | 关联冻结记录（冻结/解冻类型时必填） |
| remark | VARCHAR(256) | | 备注 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引:**
- `idx_transactions_user_id_created_at` ON (user_id, created_at DESC) — 明细查询
- `idx_transactions_type` ON (type) — 按类型筛选

### 2.3 freezes（冻结记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGSERIAL | PK | 主键 |
| user_id | VARCHAR(64) | NOT NULL, INDEX | 用户标识 |
| amount | BIGINT | NOT NULL, CHECK (> 0) | 冻结金额 |
| status | VARCHAR(16) | NOT NULL, DEFAULT 'active' | active / released / deducted |
| idempotent_key | VARCHAR(128) | NOT NULL, UNIQUE | 幂等键 |
| frozen_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 冻结时间 |
| expires_at | TIMESTAMPTZ | NOT NULL | 超时自动释放时间 |
| released_at | TIMESTAMPTZ | | 实际释放/扣减时间 |
| remark | VARCHAR(256) | | 备注 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引:**
- `idx_freezes_user_id_status` ON (user_id, status)
- `idx_freezes_expires_at` ON (expires_at) WHERE status = 'active' — 超时扫描

## 3. 并发控制方案

### 3.1 扣减场景（spend / freeze）

采用 **行级锁 (SELECT FOR UPDATE)** + **乐观锁版本号** 混合方案：

```
BEGIN;
  -- Step 1: 行锁读取账户
  SELECT id, balance, frozen_balance, version
  FROM accounts
  WHERE user_id = $1
  FOR UPDATE;

  -- Step 2: 幂等检查
  SELECT id FROM transactions WHERE idempotent_key = $2;
  IF found → ROLLBACK, 返回已有结果

  -- Step 3: 余额校验
  IF balance < amount → ROLLBACK, 返回余额不足

  -- Step 4: 更新余额 + 版本号
  UPDATE accounts
  SET balance = balance - $3, version = version + 1, updated_at = NOW()
  WHERE user_id = $1 AND version = $4;

  -- Step 5: 写入流水
  INSERT INTO transactions (...) VALUES (...);

  -- Step 6: 若为冻结，写入冻结记录
  INSERT INTO freezes (...) VALUES (...);

COMMIT;
```

**为什么需要 FOR UPDATE + 版本号？**
- `FOR UPDATE` 阻止并发写，保证同一用户的扣减操作串行化，防止超卖。
- `version` 作为额外安全网，在 ORM 场景下可替代 FOR UPDATE 做乐观锁（适合读多写少场景），但在本系统中作为双重校验保留。

### 3.2 获取场景（earn）

获取积分不需要行锁，使用 `UPDATE ... SET balance = balance + $1` 原子操作：

```
BEGIN;
  -- Step 1: 幂等检查
  -- Step 2: 确认账户存在，不存在则创建
  -- Step 3: 原子增加余额（无需 SELECT FOR UPDATE，无超卖风险）
  UPDATE accounts SET balance = balance + $1, total_earned = total_earned + $1,
         version = version + 1, updated_at = NOW()
  WHERE user_id = $2;
  -- Step 4: 写入流水
COMMIT;
```

### 3.3 并发隔离级别

- 使用 **READ COMMITTED** 级别（PostgreSQL 默认）
- 行锁 `FOR UPDATE` 保证扣减操作的串行化
- 避免使用 `SERIALIZABLE` 以减少性能开销和重试复杂度

## 4. 幂等机制

- 客户端每次请求生成唯一的 `idempotent_key`（建议格式: `{operation}:{user_id}:{uuid_v4}`）
- 服务端在 `transactions` 和 `freezes` 表上设置 `UNIQUE(idempotent_key)` 约束
- 重复请求：INSERT 冲突 → 返回已有结果（查询原 transaction/freeze 记录）
- 幂等 key 不依赖于数据库自增 ID，由客户端控制

## 5. 冻结超时自动释放

### 5.1 定时任务

每 30 秒扫描一次 `freezes` 表中 `status = 'active' AND expires_at < NOW()` 的记录：

```
-- 获取超时冻结记录
SELECT id, user_id, amount, idempotent_key
FROM freezes
WHERE status = 'active' AND expires_at < NOW()
LIMIT 100;

-- 对每条记录执行释放
BEGIN;
  SELECT * FROM accounts WHERE user_id = $1 FOR UPDATE;
  UPDATE accounts SET balance = balance + $2, frozen_balance = frozen_balance - $2,
         version = version + 1, updated_at = NOW()
  WHERE user_id = $1;
  INSERT INTO transactions (type='unfreeze', ...) VALUES (...);
  UPDATE freezes SET status = 'released', released_at = NOW() WHERE id = $3;
COMMIT;
```

### 5.2 并发安全

- 定时任务执行前，再次检查 `status = 'active'`（防竞态：用户手动解冻与定时任务同时触发）
- 使用行锁保证释放操作的原子性

## 6. 数据流

### 6.1 积分获取

```
Client → API → [幂等校验] → [账户存在?] → [原子增加余额] → [写流水] → 返回
                      ↑ 不存在则创建账户
```

### 6.2 积分消费

```
Client → API → [幂等校验] → [SELECT FOR UPDATE] → [余额校验] → [扣减余额] → [写流水] → 返回
                                                     ↓ 不足
                                                  返回错误
```

### 6.3 积分冻结

```
Client → API → [幂等校验] → [SELECT FOR UPDATE] → [余额校验] → [扣减余额+增加冻结额]
                                                               → [写流水(类型=freeze)]
                                                               → [写冻结记录] → 返回
```

### 6.4 冻结解冻

```
Client → API → [幂等校验] → [查询冻结记录] → [状态校验=active] → [SELECT FOR UPDATE]
          → [增加余额+减少冻结额] → [写流水(类型=unfreeze)] → [更新冻结状态=released] → 返回
```

### 6.5 冻结扣减

```
Client → API → [幂等校验] → [查询冻结记录] → [状态校验=active] → [SELECT FOR UPDATE]
          → [减少冻结额] → [写流水(类型=frozen_deduct)] → [更新冻结状态=deducted] → 返回
```

### 6.6 积分明细查询

```
Client → API → [SELECT * FROM transactions WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3]
              → 返回分页结果
```

## 7. 技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 数据库 | PostgreSQL 14+ | 行锁成熟、JSON 字段支持、定时任务可用 pg_cron |
| ORM | Prisma 5.x | 类型安全、迁移管理 |
| 定时任务 | pg_cron 或 应用层 Cron | 扫描超时冻结 |
| 缓存 | Redis (可选) | 热点用户余额缓存（后续优化） |
