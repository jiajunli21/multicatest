# 用户积分系统 — 架构设计

## 1. 概述

本系统为用户积分系统，支持积分获取（earn）、消费（spend）、冻结/解冻（freeze/unfreeze），以及积分余额与明细查询。积分属于资金等价物，设计上以 ACID 事务保证数据绝对一致，以乐观锁应对高并发竞争。

## 2. 存储选型

### 2.1 主存储：MySQL 8.0

**选择理由：**

- **ACID 强一致**：积分等同资金数据，不可容忍丢失或重复。MySQL InnoDB 提供完整的事务提交与崩溃恢复能力。
- **行级锁 + MVCC**：InnoDB 的 MVCC 在读多写少场景下性能优秀，行级锁粒度细，与乐观锁策略配合良好。
- **成熟运维生态**：主从复制、备份恢复、慢查询分析等运维工具链完善。

### 2.2 为何不用 Redis 做主存储

- Redis AOF/RDB 持久化本质是异步的，极端情况下可能丢失最近数秒的写入数据。
- 积分系统每笔交易都不可丢失（资金等价物），Redis 无法提供与关系型数据库同等的持久性保证。
- Redis 仅作为二级缓存层（热点账户查询加速），不参与任何写入路径。

### 2.3 技术栈

| 组件 | 选型 | 用途 |
|------|------|------|
| 数据库 | MySQL 8.0 | 主存储，全部积分数据 |
| 缓存 | Redis | 热点账户余额缓存，TTL 60s |
| 锁策略 | 乐观锁 (version) | 并发控制 |
| ORM | MyBatis-Plus / JPA | 数据访问 |

## 3. 数据模型

### 3.1 积分状态机

```
                 earn
                  │
                  ▼
           ┌──────────────┐
           │  total_points │
           │      =        │
           │ available +   │
           │   frozen      │
           └──┬────────┬──┘
              │        │
         spend│        │freeze/unfreeze
              ▼        ▼
         total_points  frozen_points
           -amount       ⇄
                    (仅在 freeze/unfreeze
                     之间转移)
```

- **可用积分 (available)** = `total_points - frozen_points`，这是实时计算值，不存在数据库列中。
- earn/spend 仅作用于 available（通过调整 total_points 实现），freeze/unfreeze 仅调整 frozen_points。

### 3.2 表结构

#### 3.2.1 user_points（用户积分表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| user_id | VARCHAR(64) | PRIMARY KEY | 用户唯一标识 |
| total_points | BIGINT | NOT NULL DEFAULT 0 | 总积分（最小单位，如分） |
| frozen_points | BIGINT | NOT NULL DEFAULT 0 | 冻结积分 |
| version | INT | NOT NULL DEFAULT 0 | 乐观锁版本号 |
| created_at | DATETIME(3) | NOT NULL | 创建时间 |
| updated_at | DATETIME(3) | NOT NULL | 最后更新时间 |

- available_points = total_points - frozen_points（动态计算）
- 所有金额单位统一为分（整数），避免浮点精度问题

#### 3.2.2 points_transaction（积分流水表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PRIMARY KEY AUTO_INCREMENT | 流水 ID |
| user_id | VARCHAR(64) | NOT NULL | 用户标识 |
| type | ENUM('earn','spend','freeze','unfreeze') | NOT NULL | 操作类型 |
| amount | BIGINT | NOT NULL | 变动金额（正数） |
| balance_before | BIGINT | NOT NULL | 操作前 total_points |
| balance_after | BIGINT | NOT NULL | 操作后 total_points |
| reference_id | VARCHAR(128) | NOT NULL | 幂等键（业务方生成） |
| description | VARCHAR(256) | DEFAULT NULL | 备注说明 |
| created_at | DATETIME(3) | NOT NULL DEFAULT CURRENT_TIMESTAMP(3) | 创建时间 |

- `reference_id` 全局唯一约束，防止重复入账/扣款

#### 3.2.3 points_freeze_record（冻结记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PRIMARY KEY AUTO_INCREMENT | 冻结记录 ID |
| user_id | VARCHAR(64) | NOT NULL | 用户标识 |
| amount | BIGINT | NOT NULL | 冻结金额 |
| status | ENUM('frozen','unfrozen') | NOT NULL DEFAULT 'frozen' | 状态 |
| reason | VARCHAR(256) | DEFAULT NULL | 冻结原因 |
| created_at | DATETIME(3) | NOT NULL DEFAULT CURRENT_TIMESTAMP(3) | 创建时间 |
| unfrozen_at | DATETIME(3) | DEFAULT NULL | 解冻时间 |

### 3.3 索引设计

```sql
-- user_points
PRIMARY KEY (user_id)

-- points_transaction
UNIQUE KEY uk_reference_id (reference_id)          -- 幂等去重
INDEX idx_user_created (user_id, created_at DESC)  -- 明细分页查询

-- points_freeze_record
INDEX idx_user_status (user_id, status)            -- 查询活跃冻结
```

**索引设计说明：**
- `uk_reference_id` 是幂等核心保障，重复相同 reference_id 的业务请求直接返回已有交易，不产生副作用
- `idx_user_created` 覆盖积分明细分页查询（WHERE user_id = ? ORDER BY created_at DESC）
- `idx_user_status` 覆盖"查询某用户当前冻结记录"场景

## 4. 数据流设计

所有写操作（earn/spend/freeze/unfreeze）必须在同一数据库事务内完成，遵循"幂等检查 → 数据校验 → 乐观锁更新 → 写流水"的原子流程。

### 4.1 积分获取 (earn)

```
Client → POST /api/v1/points/earn
           │
           ▼
      ┌─────────────────┐
      │ 1. 幂等检查       │──reference_id 已存在? → 直接返回已有结果
      │ 2. 校验 amount>0  │
      │ 3. BEGIN TX      │
      │ 4. SELECT        │  user_points WHERE user_id
      │    total_points,  │  (不存在则 INSERT 初始化)
      │    frozen_points, │
      │    version        │
      │ 5. new_total =   │
      │    total + amount │
      │ 6. UPDATE        │  user_points SET total_points=new_total,
      │                  │  version=version+1
      │                  │  WHERE user_id=? AND version=?
      │ 7. affected=0?   │──→ 乐观锁冲突，重试（最多3次）
      │ 8. INSERT        │  points_transaction (type=earn)
      │ 9. COMMIT        │
      └─────────────────┘
           │
           ▼
      Response: { user_id, amount, balance_after, transaction_id }
```

### 4.2 积分消费 (spend)

```
流程同 earn，差异点：
  - 步骤 2 额外校验: (total_points - frozen_points) >= amount
    不满足 → INSUFFICIENT_BALANCE
  - 步骤 5: new_total = total_points - amount
  - 步骤 8: type=spend
```

### 4.3 积分冻结 (freeze)

```
      ┌─────────────────┐
      │ 1. 幂等检查       │
      │ 2. 校验 amount>0  │
      │ 3. BEGIN TX      │
      │ 4. SELECT        │  user_points
      │ 5. 校验:         │
      │   total_points    │
      │   - frozen_points │
      │   >= amount       │──→ 不满足: INSUFFICIENT_AVAILABLE_BALANCE
      │ 6. UPDATE        │  user_points
      │   frozen_points = │  SET frozen_points=frozen_points+amount,
      │   frozen+amount,  │  version=version+1
      │   version+1       │  WHERE user_id=? AND version=?
      │ 7. 乐观锁冲突重试  │
      │ 8. INSERT        │  points_freeze_record (status=frozen)
      │ 9. INSERT        │  points_transaction (type=freeze)
      │10. COMMIT        │
      └─────────────────┘
```

### 4.4 积分解冻 (unfreeze)

```
      ┌─────────────────┐
      │ 1. 幂等检查       │
      │ 2. BEGIN TX      │
      │ 3. SELECT        │  points_freeze_record WHERE id=?
      │ 4. 校验:         │
      │   记录存在          │──→ 不存在: FREEZE_RECORD_NOT_FOUND
      │   status=frozen   │──→ 已解冻: ALREADY_UNFROZEN
      │ 5. SELECT+UPDATE │  user_points
      │   frozen_points = │  (乐观锁)
      │   frozen-amount   │
      │ 6. UPDATE        │  points_freeze_record
      │   status=unfrozen,│  SET status='unfrozen', unfrozen_at=NOW()
      │   unfrozen_at    │
      │ 7. 乐观锁冲突重试  │
      │ 8. INSERT        │  points_transaction (type=unfreeze)
      │ 9. COMMIT        │
      └─────────────────┘
```

### 4.5 查询数据流

```
余额查询 GET /balance/{user_id}:
  Redis (TTL 60s) → 命中则直接返回
                   → 未命中 → MySQL 查询 → 写入 Redis

明细查询 GET /transactions/{user_id}?page=&page_size=&type=:
  直接查 MySQL，利用 idx_user_created 索引分页
  (流水表写多读少，不做 Redis 缓存，避免缓存穿透)
```

## 5. 并发控制

### 5.1 乐观锁机制

所有积分变更操作使用乐观锁（version 字段）：

```sql
UPDATE user_points
SET total_points = ?, version = version + 1, updated_at = NOW(3)
WHERE user_id = ? AND version = ?;
```

- 执行后检查 `affected_rows = 0` 表示版本冲突
- 冲突时重试整个事务（重新读取 + 计算 + 更新），最多 **3 次**
- 3 次均失败则返回 `CONCURRENCY_CONFLICT` 错误码，由调用方决定是否重试

### 5.2 为何不用悲观锁

- `SELECT ... FOR UPDATE` 在同一用户高并发操作时会导致**锁等待甚至死锁**，TPS 严重退化。
- 积分系统的并发热点集中在少数活跃用户，悲观锁会让这些用户的请求串行化，吞吐量受到单行锁瓶颈限制。
- 乐观锁的优势：无锁等待，冲突时仅重试少量操作，在低冲突率场景（大多数用户并发度不高）下吞吐量远优于悲观锁。
- 实际业务中同一用户同时发起多个积分操作的概率较低，乐观锁冲突率通常 << 1%，重试代价可忽略。

### 5.3 幂等性保障

- 所有写操作由调用方提供 `reference_id`（业务幂等键，如订单号）
- `points_transaction.reference_id` 建立 UNIQUE 约束
- 重复的 `reference_id` 在 INSERT 时触发唯一约束冲突：
  - 事务内捕获 `DuplicateKeyException`
  - 查询已有 transaction 并直接返回成功结果
- 幂等键粒度由业务方控制，本系统仅保证存储层幂等

## 6. 缓存策略

### 6.1 热点账户缓存

```
Redis key:  points:balance:{user_id}
Value:      JSON { total_points, frozen_points, version }
TTL:        60s（短期，减少不一致窗口）
更新策略:   Cache-Aside
  - 写操作: 事务提交后 DEL key（主动失效）
  - 读操作: 先查 Redis → 未命中则查 MySQL → SET key EX 60
```

### 6.2 冷热分离

- **热数据（Redis）**：活跃用户的余额缓存，读多写少
- **温数据（MySQL）**：全部账户 + 近期流水，走索引查询
- **冷数据（归档）**：超过 90 天的流水可按月归档到历史表或对象存储

### 6.3 缓存一致性权衡

- 缓存 TTL 设为 60s，极端情况下余额展示有最多 60s 延迟
- 积分变更操作直接穿透到 MySQL，不做缓存写入（仅失效），避免缓存与 DB 的复杂一致性问题
- 查询方应接受"余额为最终一致性"，扣款校验走 DB 事务保证强一致

## 7. 错误码体系

| 错误码 | HTTP 状态 | 场景 |
|--------|----------|------|
| INSUFFICIENT_BALANCE | 400 | 消费时可用余额不足 |
| INSUFFICIENT_AVAILABLE_BALANCE | 400 | 冻结时可用余额不足 |
| FREEZE_RECORD_NOT_FOUND | 404 | 解冻时冻结记录不存在 |
| ALREADY_UNFROZEN | 409 | 重复解冻 |
| CONCURRENCY_CONFLICT | 409 | 乐观锁重试 3 次均失败 |
| DUPLICATE_REFERENCE_ID | 409 | 幂等冲突（实际返回原结果） |
| INVALID_AMOUNT | 400 | amount ≤ 0 |
| USER_NOT_FOUND | 404 | 用户不存在 |

## 8. 数据一致性约束

以下等式在任何时刻应当成立：

- `available_points = total_points - frozen_points ≥ 0`
- `total_points = SUM(points_transaction.amount WHERE type IN ('earn', 'spend'))` — 仅在 earn/spend 有 signed 含义时成立（实际 amount 存储正数，type 表明方向）
- `frozen_points = SUM(points_freeze_record.amount WHERE status = 'frozen')`
