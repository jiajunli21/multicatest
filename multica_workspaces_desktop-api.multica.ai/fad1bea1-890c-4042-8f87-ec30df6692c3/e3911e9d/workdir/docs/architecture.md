# 用户积分系统 — 架构文档

> 产出阶段：BEW-3（架构与数据编排）
> 生成时间：2026-05-14
> 上游输入：BEW-2（.multica/plan.md / docs/plan.md）

## 1. 技术选型

| 层级 | 选型 | 理由 |
|------|------|------|
| 语言 | TypeScript / Node.js | 生态成熟，Prisma ORM 对 PostgreSQL 支持完善 |
| 运行时 | Node.js 18+ | LTS 版本 |
| 框架 | Express 或 Fastify | 轻量 HTTP 框架，路由清晰 |
| ORM | Prisma | 类型安全、迁移管理、Schema 即文档 |
| 数据库 | PostgreSQL 14+ | ACID 事务、行级锁、JSONB 支持，适合积分/账务场景 |
| 缓存 | Redis（可选，本期不强制） | 用于热点账户余额缓存，减轻 DB 读压力 |

## 2. 模块划分

```
src/
├── modules/
│   └── points/
│       ├── points.controller.ts    # HTTP 路由与请求解析
│       ├── points.service.ts       # 核心业务逻辑（获取/消费/冻结/解冻/扣减）
│       ├── points.repository.ts    # 数据访问层（Prisma 查询封装）
│       ├── points.validator.ts     # 请求参数校验
│       └── points.errors.ts        # 领域错误定义
├── common/
│   ├── prisma/
│   │   └── schema.prisma           # 数据库 Schema（或独立于 src 的 prisma/ 目录）
│   ├── errors.ts                   # 全局错误处理
│   └── pagination.ts               # 分页工具
└── app.ts                          # 应用入口
```

**模块职责边界：**

| 模块 | 负责 | 不负责 |
|------|------|--------|
| Controller | 解析 HTTP 请求，调用 Service，格式化响应 | 业务逻辑、数据访问 |
| Service | 业务逻辑编排、余额校验、状态流转、幂等控制 | HTTP 细节、原生 SQL |
| Repository | 数据库读写、乐观锁处理、事务管理 | 业务规则判断 |
| Validator | 请求参数校验（金额 > 0、必填字段等） | 业务规则（余额是否充足） |

## 3. 核心数据流

### 3.1 积分获取（EARN）

```
HTTP POST /api/v1/points/earn
  → Controller: 解析 body (user_id, amount, source, reference_id, expires_at?)
  → Validator: 校验 amount > 0, 必填字段
  → Service.earn():
    1. 幂等检查: 查询 reference_id 是否已处理 → 已处理则直接返回现有结果
    2. 账户查询: 查 PointAccount by user_id, 不存在则 lazy create
    3. 写入明细: INSERT PointTransaction (type=EARN)
    4. 更新账户: UPDATE available_balance += amount, total_earned += amount, version += 1
       WHERE version = old_version（乐观锁）
    5. 乐观锁冲突 → 重试（最多 3 次）
  → Controller: 返回 { available_balance, frozen_balance }
```

### 3.2 积分消费（SPEND）

```
HTTP POST /api/v1/points/spend
  → Controller: 解析 body (user_id, amount, reference_id)
  → Validator: 校验 amount > 0
  → Service.spend():
    1. 幂等检查
    2. 查询账户，校验 available_balance >= amount → 不足则抛 INSUFFICIENT_BALANCE
    3. 查询未过期 EARN 明细，按 expires_at ASC 排序，逐条扣减
       （FIFO/优先消费即将过期积分）
    4. 写入 SPEND 明细（多条，对应每条被扣减的 EARN 记录）
    5. 更新账户: available_balance -= amount, total_spent += amount, version += 1
       WHERE version = old_version
    6. 乐观锁冲突 → 重试
  → Controller: 返回 { available_balance, frozen_balance, consumed_details }
```

### 3.3 积分冻结（FREEZE）

```
HTTP POST /api/v1/points/freeze
  → Service.freeze():
    1. 幂等检查
    2. 查询账户，校验 available_balance >= amount
    3. 创建 FreezeRecord (status=ACTIVE, remaining=amount)
    4. 写入 FREEZE 明细
    5. 更新账户: available_balance -= amount, frozen_balance += amount（乐观锁）
  → Controller: 返回 { freeze_record_id, available_balance, frozen_balance }
```

### 3.4 积分解冻（UNFREEZE）

```
HTTP POST /api/v1/points/unfreeze
  → Service.unfreeze():
    1. 幂等检查
    2. 查询 FreezeRecord，校验 status=ACTIVE 且 remaining >= amount
    3. 更新 FreezeRecord: remaining -= amount, 若 remaining == 0 则 status=RELEASED
    4. 写入 UNFREEZE 明细
    5. 更新账户: available_balance += amount, frozen_balance -= amount（乐观锁）
```

### 3.5 冻结积分扣减（DEDUCT_FROZEN）

```
HTTP POST /api/v1/points/deduct-frozen
  → Service.deductFrozen():
    1. 幂等检查
    2. 查询 FreezeRecord，校验 status=ACTIVE 且 remaining >= amount
    3. 更新 FreezeRecord: remaining -= amount, 若 remaining == 0 则 status=DEDUCTED
    4. 写入 DEDUCT 明细（注意: 不影响可用余额）
    5. 更新账户: frozen_balance -= amount（乐观锁）
```

### 3.6 余额查询（BALANCE）

```
HTTP GET /api/v1/points/balance?user_id=xxx
  → Controller → Service.getBalance():
    1. 查询 PointAccount by user_id
    2. 不存在则返回 { available: 0, frozen: 0, total: 0 }
    3. 存在则返回 { available_balance, frozen_balance, total }
```

### 3.7 明细查询（TRANSACTIONS）

```
HTTP GET /api/v1/points/transactions?user_id=xxx&type=EARN&since=...&until=...&page=1&page_size=20
  → Controller → Service.listTransactions():
    1. 查询 PointTransaction，支持筛选、分页
    2. 按 created_at DESC 排序
    3. 返回 { items, total, page, page_size, has_more }
```

## 4. 数据模型

### 4.1 PointAccount（积分账户）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 主键 |
| user_id | VARCHAR(64) | UNIQUE, NOT NULL | 用户 ID |
| available_balance | BIGINT | NOT NULL, DEFAULT 0, CHECK >= 0 | 可用积分余额 |
| frozen_balance | BIGINT | NOT NULL, DEFAULT 0, CHECK >= 0 | 冻结积分余额 |
| total_earned | BIGINT | NOT NULL, DEFAULT 0, CHECK >= 0 | 累计获取积分 |
| total_spent | BIGINT | NOT NULL, DEFAULT 0, CHECK >= 0 | 累计消费积分 |
| version | INTEGER | NOT NULL, DEFAULT 1 | 乐观锁版本号 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

索引：
- UNIQUE INDEX on `user_id`
- 无额外索引（user_id 为主查询键，已有唯一索引）

### 4.2 PointTransaction（积分明细）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 主键 |
| user_id | VARCHAR(64) | NOT NULL | 用户 ID |
| type | point_txn_type | NOT NULL | 变动类型 |
| amount | BIGINT | NOT NULL, CHECK > 0 | 变动金额（正数） |
| balance_after | BIGINT | NOT NULL | 变动后可用余额快照 |
| frozen_after | BIGINT | NOT NULL | 变动后冻结余额快照 |
| source | VARCHAR(64) | NOT NULL, DEFAULT '' | 来源渠道 |
| reference_id | VARCHAR(128) | NOT NULL | 关联业务单号（幂等键） |
| expires_at | TIMESTAMPTZ | 可为 NULL | 过期时间（仅 EARN 有效） |
| metadata | JSONB | NOT NULL, DEFAULT '{}' | 扩展信息 |
| freeze_record_id | UUID | 可为 NULL, FK → freeze_records | 关联冻结记录（FREEZE/UNFREEZE/DEDUCT 时填写） |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |

索引：
- INDEX on `(user_id, created_at DESC)` — 明细列表分页查询
- UNIQUE INDEX on `(user_id, type, reference_id)` — 幂等控制
- INDEX on `(expires_at)` WHERE type = 'EARN' AND expires_at IS NOT NULL — 过期积分查询

枚举 `point_txn_type`：
- `EARN` — 积分获取
- `SPEND` — 积分消费
- `FREEZE` — 积分冻结
- `UNFREEZE` — 积分解冻
- `DEDUCT` — 冻结积分扣减

### 4.3 FreezeRecord（冻结记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, DEFAULT gen_random_uuid() | 主键 |
| user_id | VARCHAR(64) | NOT NULL | 用户 ID |
| amount | BIGINT | NOT NULL, CHECK > 0 | 初始冻结金额 |
| remaining | BIGINT | NOT NULL, CHECK >= 0 | 剩余冻结金额 |
| reason | VARCHAR(256) | NOT NULL, DEFAULT '' | 冻结原因 |
| operator_id | VARCHAR(64) | NOT NULL | 操作人 ID |
| status | freeze_status | NOT NULL, DEFAULT 'ACTIVE' | 冻结状态 |
| metadata | JSONB | NOT NULL, DEFAULT '{}' | 扩展信息 |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | 更新时间 |

索引：
- INDEX on `(user_id, status)` — 按用户查询活跃冻结记录
- INDEX on `(status, created_at)` — 管理后台查询

枚举 `freeze_status`：
- `ACTIVE` — 冻结中
- `RELEASED` — 已解冻
- `DEDUCTED` — 已扣减

## 5. 状态流转规则

### 5.1 PointAccount（账户余额）

账户本身无状态机，只有余额数值的变化：

```
available_balance: 初始 0, 只能通过 EARN / UNFREEZE 增加, 通过 SPEND / FREEZE 减少
frozen_balance:   初始 0, 只能通过 FREEZE 增加, 通过 UNFREEZE / DEDUCT 减少
total_earned:     初始 0, 仅 EARN 时递增, 永不减少
total_spent:      初始 0, 仅 SPEND 时递增, 永不减少
```

不变量：
- `available_balance >= 0`
- `frozen_balance >= 0`
- `total_earned >= total_spent + available_balance + frozen_balance`（允许部分积分已过期未扣除）

### 5.2 FreezeRecord（冻结状态机）

```
                    ┌──────────┐
                    │  ACTIVE  │
                    └────┬──┬──┘
             解冻全部   │  │  扣减全部
                    ┌───┘  └───┐
               ┌────┴──┐  ┌───┴──────┐
               │RELEASED│  │ DEDUCTED │
               └────────┘  └──────────┘
```

转换规则：
- `ACTIVE → RELEASED`：remaining 降至 0 时自动（全部解冻）
- `ACTIVE → DEDUCTED`：remaining 降至 0 时自动（全部扣减）
- 部分解冻/扣减时状态保持 ACTIVE，仅递减 remaining
- 不允许从 RELEASED / DEDUCTED 回退到 ACTIVE

### 5.3 积分过期（本期不自动执行）

- 过期由外部调度系统触发
- 系统提供查询接口：按 `expires_at < NOW()` 且 `type = EARN` 且仍有剩余可扣减量的明细
- 过期执行逻辑由业务层定义（扣除/失效），本系统预留过期查询能力

## 6. 数据存储结构（PostgreSQL DDL）

详见 `docs/schema.sql`。

三表结构：
- `point_accounts` — 积分账户（与 user_id 一一对应）
- `point_transactions` — 积分变动明细（只追加，不修改，不删除）
- `freeze_records` — 冻结记录（状态可变）

存储原则：
- 明细表只追加（append-only），不可修改和删除，保证审计完整性
- 账户表使用乐观锁（version 列）防止并发写冲突
- 幂等由 `(user_id, type, reference_id)` 联合唯一约束保证

## 7. 查询与写入边界

### 7.1 写入边界

| 操作 | 写入目标 | 事务范围 |
|------|----------|----------|
| EARN | PointTransaction + PointAccount（如首次则 lazy create） | 同一事务 |
| SPEND | PointTransaction（可多条） + PointAccount | 同一事务 |
| FREEZE | PointTransaction + FreezeRecord + PointAccount | 同一事务 |
| UNFREEZE | PointTransaction + FreezeRecord + PointAccount | 同一事务 |
| DEDUCT | PointTransaction + FreezeRecord + PointAccount | 同一事务 |

所有写操作必须在事务内完成，失败时整体回滚。

### 7.2 查询边界

| 查询 | 数据来源 | 说明 |
|------|----------|------|
| 用户余额 | PointAccount | 单行查询，user_id 唯一索引 |
| 用户明细列表 | PointTransaction | 分页，user_id + created_at 联合索引 |
| 即将过期积分 | PointTransaction | expires_at 条件索引 |
| 用户冻结记录 | FreezeRecord | 分页，user_id + status 联合索引 |

### 7.3 读写分离（本期不强制）

- 余额查询可读从库（如部署了只读副本）
- 所有写操作和涉及余额校验的读（如 SPEND 前的余额检查）必须走主库

## 8. 一致性与并发风险

### 8.1 并发消费场景（最重要风险）

**场景：** 同一用户的两个消费请求同时到达，各自校验余额充足后同时扣减，导致超扣。

**缓解措施：**
1. **乐观锁（应用层）：** 更新 PointAccount 时带 `WHERE version = :old_version`，冲突时重试（最多 3 次）
2. **SELECT ... FOR UPDATE（数据库层）：** 在 Service 中对 PointAccount 行加悲观锁，确保同一用户的写操作串行化
3. **推荐策略：** 乐观锁重试为主 + 悲观锁为辅（超过重试次数后降级为悲观锁）

### 8.2 幂等性

**唯一约束：** `(user_id, type, reference_id)` ON `point_transactions`

- 同一业务单号不可重复处理
- 幂等返回时应返回与原请求一致的响应结构
- 首次请求成功返回后，后续相同 reference_id 直接返回已有结果

### 8.3 冻结与消费的竞态

**场景：** 冻结和消费同时发生，余额分配可能出现竞争。

**缓解：** 冻结和消费操作同一用户的 PointAccount 行，数据库行锁自然串行化。应用层保证冻结和消费都在事务内先获取行锁。

### 8.4 余额一致性

**不变量检查（可周期性执行）：**
- `available_balance` = SUM(EARN + UNFREEZE) - SUM(SPEND + FREEZE) — 考虑过期
- `frozen_balance` = SUM(FREEZE) - SUM(UNFREEZE + DEDUCT)
- `total_earned` >= `total_spent`

### 8.5 其他风险

| 风险 | 缓解 |
|------|------|
| 冻结记录与账户余额不一致 | 冻结/解冻/扣减在同一事务内更新 freeze_records 和 point_accounts |
| 明细与余额快照不匹配 | balance_after / frozen_after 在事务内写入，与账户更新同批次 |
| 大金额操作 | 应用层校验单次金额 ≤ 可配置上限（默认 1,000,000 分） |
| 账户不存在时的写操作 | 首次 EARN 时 lazy create 账户，其他操作类型遇账户不存在应报错 |

## 9. 下游接口契约输入说明

### 9.1 BEW-4（接口契约）需要覆盖的对象

**请求对象：**
- `EarnRequest`: user_id, amount, source, reference_id, expires_at?
- `SpendRequest`: user_id, amount, reference_id
- `FreezeRequest`: user_id, amount, reason, operator_id, reference_id
- `UnfreezeRequest`: freeze_record_id, amount, reference_id
- `DeductFrozenRequest`: freeze_record_id, amount, reference_id

**响应对象：**
- `BalanceResponse`: user_id, available_balance, frozen_balance
- `TransactionItem`: id, type, amount, balance_after, frozen_after, source, reference_id, created_at
- `TransactionListResponse`: items[], total, page, page_size, has_more
- `OperationResult`: success, data (含操作后的余额/冻结记录)

**查询参数：**
- 余额查询: user_id
- 明细查询: user_id, type?, since?, until?, page?, page_size?

### 9.2 BEW-4 需要覆盖的动作

| HTTP 方法 | 路径 | 动作 |
|-----------|------|------|
| POST | /api/v1/points/earn | 积分获取 |
| POST | /api/v1/points/spend | 积分消费 |
| POST | /api/v1/points/freeze | 积分冻结 |
| POST | /api/v1/points/unfreeze | 积分解冻 |
| POST | /api/v1/points/deduct-frozen | 冻结积分扣减 |
| GET | /api/v1/points/balance | 查询余额 |
| GET | /api/v1/points/transactions | 查询明细 |

### 9.3 BEW-4 错误码建议

| 错误码 | 含义 | 触发条件 |
|--------|------|----------|
| INSUFFICIENT_BALANCE | 余额不足 | SPEND 时 available_balance < amount |
| ACCOUNT_NOT_FOUND | 账户不存在 | SPEND/FREEZE 时用户无账户 |
| FREEZE_RECORD_NOT_FOUND | 冻结记录不存在 | UNFREEZE/DEDUCT 时 freeze_record 无效 |
| FREEZE_NOT_ACTIVE | 冻结记录非活跃 | UNFREEZE/DEDUCT 时 status != ACTIVE |
| INSUFFICIENT_FROZEN | 冻结余额不足 | UNFREEZE/DEDUCT 时 remaining < amount |
| DUPLICATE_REFERENCE | 重复业务单号 | 幂等命中 |
| AMOUNT_EXCEEDS_LIMIT | 金额超限 | amount > 配置上限 |
| INVALID_AMOUNT | 金额无效 | amount <= 0 |
| VERSION_CONFLICT | 并发冲突（内部重试耗尽） | 乐观锁重试 3 次后仍失败 |

## 10. 扩展预留

以下内容在 Schema 和模型中已预留，本期不实现：

- **多积分类型：** PointAccount 可扩展 `point_type` 字段（当前仅 SINGLE），支持同一用户持有多种积分
- **事件发布：** 积分变动后可向消息队列发布事件（预留 `PointEvent` 结构）
- **积分过期自动执行：** Schema 中 expires_at 和对应索引已就位，外部调度器可消费

## 11. 关键决策记录

1. **PostgreSQL + 悲观行锁**：积分涉及资金类操作，一致性优先于性能，选择 PostgreSQL 利用其行级锁和事务保证
2. **明细表只追加（append-only）**：审计完整性要求，不可物理删除或修改历史明细
3. **乐观锁 + 重试作为主策略**：高并发下乐观锁比悲观锁吞吐更高，仅在重试耗尽时降级到悲观锁
4. **账户 lazy creation**：避免海量空账户预创建，首次获取时按需创建
5. **int64 存储金额，单位"分"**：避免浮点精度问题
6. **JSONB metadata**：为业务方预留扩展空间，不限制额外自定义字段
7. **语言/框架选型为 TypeScript + Prisma**：类型安全 + Schema 即文档，适合流水线式开发（BEW-4 可直接引用 Prisma Schema 中的类型）
