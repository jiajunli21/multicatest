# 用户积分系统 — 实施计划

## 概述

构建一个用户积分系统，支持积分获取、消费、冻结/解冻，以及积分明细查询。

---

## 阶段一：架构设计（WS-36）

**职责**: 架构与数据编排 Agent
**输入**: 本 plan.md
**输出**: `docs/architecture.md` + 数据库 Schema

### 验收标准

1. **数据模型设计**
   - [ ] `user_points` 表：`user_id`（唯一索引）、`total_points`、`frozen_points`、`version`（乐观锁）、`created_at`、`updated_at`
   - [ ] `points_transaction` 表：`id`、`user_id`、`type`（枚举 earn/spend/freeze/unfreeze）、`amount`、`balance_before`、`balance_after`、`reference_id`（幂等键唯一索引）、`description`、`created_at`
   - [ ] `points_freeze_record` 表：`id`、`user_id`、`amount`、`status`（frozen/unfrozen）、`reason`、`created_at`、`unfrozen_at`
   - [ ] `user_id + created_at` 复合索引用于明细分页查询

2. **数据流与状态机**
   - [ ] 积分状态机：可用积分 ⇄ 冻结积分，earn/spend 操作只能作用于可用积分
   - [ ] 操作原子性边界：单次 earn/spend/freeze/unfreeze 必须在同一数据库事务内完成
   - [ ] 幂等策略：通过 `reference_id` 唯一约束防止重复入账/扣款

3. **并发控制**
   - [ ] 乐观锁（`version` 字段）：UPDATE 时校验 version，失败则重试，最多 3 次
   - [ ] 说明为何不用悲观锁（高并发下性能退化严重）

4. **存储选型**
   - [ ] 主存储：MySQL 8.0+ 或 PostgreSQL 14+（保证 ACID）
   - [ ] 说明为何不用 Redis 做主存储（积分等同资金数据，不可容忍丢失）

---

## 阶段二：接口契约（WS-37）

**职责**: 接口契约 Agent
**输入**: `docs/architecture.md`
**输出**: `docs/api_contract.json`

### 验收标准

1. **积分获取** — `POST /api/v1/points/earn`
   - [ ] 请求：`{ user_id, amount(>0), reference_id, description? }`
   - [ ] 响应：`{ user_id, amount, balance_after, transaction_id, created_at }`
   - [ ] 幂等：相同 reference_id 返回已有结果，不重复加积分

2. **积分消费** — `POST /api/v1/points/spend`
   - [ ] 请求：`{ user_id, amount(>0), reference_id, description? }`
   - [ ] 响应：`{ user_id, amount, balance_after, transaction_id, created_at }`
   - [ ] 余额不足时返回 `INSUFFICIENT_BALANCE`

3. **积分冻结** — `POST /api/v1/points/freeze`
   - [ ] 请求：`{ user_id, amount(>0), reference_id, reason? }`
   - [ ] 响应：`{ user_id, amount, freeze_record_id, available_after, frozen_after }`
   - [ ] 可用余额不足时返回 `INSUFFICIENT_AVAILABLE_BALANCE`

4. **积分解冻** — `POST /api/v1/points/unfreeze`
   - [ ] 请求：`{ user_id, freeze_record_id, reference_id }`
   - [ ] 响应：`{ user_id, amount, freeze_record_id, available_after, frozen_after }`
   - [ ] 记录不存在/已解冻时返回对应错误

5. **余额查询** — `GET /api/v1/points/balance/{user_id}`
   - [ ] 响应：`{ user_id, total_points, frozen_points, available_points }`

6. **明细查询** — `GET /api/v1/points/transactions/{user_id}?page=1&page_size=20&type=earn`
   - [ ] 响应：`{ items: [...], total, page, page_size }`
   - [ ] 支持按 type 筛选，按时间倒序

7. **通用规范**
   - [ ] 统一错误格式：`{ error_code, message }`
   - [ ] 金额统一使用整数（最小单位，如分），避免浮点精度问题
   - [ ] 完整 HTTP 状态码规范（200/400/404/409/500）

---

## 阶段三：业务实现（WS-38）

**职责**: 业务逻辑组装 Agent
**输入**: `docs/architecture.md` + `docs/api_contract.json`
**输出**: Controller + Service + Repository 代码

### 验收标准

1. **Controller 层**
   - [ ] 实现全部 6 个 API 端点
   - [ ] 请求参数校验（必填字段、amount > 0 等）
   - [ ] 统一异常处理，映射业务异常到 HTTP 响应

2. **Service 层 — earn**
   - [ ] 幂等检查（reference_id 去重）
   - [ ] 事务内：乐观锁更新 total_points → 插入 transaction 记录

3. **Service 层 — spend**
   - [ ] 幂等检查
   - [ ] 校验 `available_points >= amount`
   - [ ] 事务内：乐观锁扣减 total_points → 插入 transaction 记录

4. **Service 层 — freeze**
   - [ ] 幂等检查
   - [ ] 校验 `available_points >= amount`
   - [ ] 事务内：乐观锁增加 frozen_points → 插入 freeze_record → 插入 transaction

5. **Service 层 — unfreeze**
   - [ ] 幂等检查
   - [ ] 校验 freeze_record 存在且 status=frozen
   - [ ] 事务内：乐观锁减少 frozen_points → 更新 freeze_record → 插入 transaction

6. **Service 层 — 查询**
   - [ ] balance：查 user_points 表
   - [ ] transactions：分页查 points_transaction，支持 type 过滤

7. **Repository 层**
   - [ ] 乐观锁更新使用 `UPDATE ... WHERE version = ?`，检查 affected rows
   - [ ] 幂等查询按 reference_id 精确匹配

---

## 阶段四：测试与质量审计（WS-39）

**职责**: 稳定性与质量 Agent
**输入**: 全部已实现代码
**输出**: 测试报告 + 补充的测试用例

### 验收标准

1. **单元测试**
   - [ ] 每个 Service 方法 ≥ 3 个用例（正常、边界、异常）
   - [ ] 幂等性：相同 reference_id 重复调用无副作用
   - [ ] 乐观锁冲突模拟：版本冲突时重试生效

2. **集成测试**
   - [ ] 完整链路 earn → balance → spend → balance
   - [ ] 完整链路 earn → freeze → balance（验证 frozen/available）→ unfreeze → balance
   - [ ] 冻结后消费超过 available 余额被拒绝
   - [ ] 分页查询正确性

3. **并发测试**
   - [ ] 并发 earn：多请求同时加积分，最终总额正确
   - [ ] 并发 spend + freeze：乐观锁重试生效，数据一致

4. **边界与异常**
   - [ ] amount ≤ 0 被参数校验拦截
   - [ ] 用户不存在返回正确错误
   - [ ] 重复 reference_id 幂等返回
   - [ ] 解冻已解冻记录返回错误

5. **数据一致性**
   - [ ] `total_points = SUM(transactions WHERE type IN (earn, spend))`
   - [ ] `frozen_points = SUM(freeze_records WHERE status=frozen)`
