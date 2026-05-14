# 用户积分系统 — 实施计划

## 项目概述
构建一个用户积分系统，支持积分获取、积分消费、积分冻结/解冻，以及积分明细查询。

## 阶段依赖关系
```
[阶段1] 架构设计 ──→ [阶段2] 接口契约 ──→ [阶段3] 业务实现 ──→ [阶段4] 质量审计
```

---

## 阶段1：架构设计

### 验收标准
- [ ] 输出 `docs/architecture.md`，包含：
  - 系统整体数据流图（积分获取/消费/冻结/解冻的端到端流程）
  - 存储方案选型与理由（MySQL + Redis 缓存层）
  - 高并发下积分一致性方案（乐观锁版本号机制 + Redis 分布式锁兜底）
  - 缓存策略（热点账户积分缓存、冷热分离）
- [ ] 生成数据库 Schema 文件 `docs/db_schema.sql`，至少包含以下表：
  - **points_account**（积分账户表）：user_id, total_points, frozen_points, available_points, version, created_at, updated_at
  - **points_transaction**（积分流水表）：id, account_id, user_id, type（EARN/CONSUME/FREEZE/UNFREEZE）, amount, balance_before, balance_after, biz_id（幂等键）, biz_type, description, created_at
  - **points_freeze_record**（冻结记录表）：id, account_id, user_id, transaction_id, amount, status（FROZEN/RELEASED/DEDUCTED）, expires_at, created_at, updated_at
- [ ] 索引设计：user_id 唯一索引、biz_id 唯一索引（幂等）、流水表 (account_id, created_at) 复合索引
- [ ] 积分过期机制设计（expires_at 字段 + 定时任务扫描过期积分）
- [ ] 幂等性设计：通过 biz_id + biz_type 唯一约束防止重复入账

---

## 阶段2：接口契约

### 验收标准
- [ ] 输出 `docs/api_contract.json`（OpenAPI 3.0 规范），覆盖以下端点：
  - `POST /api/v1/points/earn` — 积分获取
  - `POST /api/v1/points/consume` — 积分消费
  - `POST /api/v1/points/freeze` — 积分冻结
  - `POST /api/v1/points/unfreeze` — 积分解冻
  - `POST /api/v1/points/deduct-frozen` — 冻结积分扣减
  - `GET /api/v1/points/balance/{userId}` — 积分余额查询
  - `GET /api/v1/points/transactions/{userId}` — 积分明细查询（分页）
- [ ] 输出 `docs/mcp_schema.md`（如果系统需要暴露为 MCP 工具，定义工具 Schema）
- [ ] 每个端点包含完整的 Request/Response Schema、错误码映射
- [ ] 错误码至少覆盖：参数校验失败、账户不存在、积分不足、冻结记录不存在/已过期、重复请求（幂等冲突）、并发冲突
- [ ] 分页查询支持 cursor 或 offset/pageNo 分页

---

## 阶段3：业务实现

### 验收标准
- [ ] 编写 Controller 层代码（Spring Boot 3.x + JDK 17+）：
  - PointsController：暴露上述 7 个 REST 端点
  - 统一异常处理（GlobalExceptionHandler）
  - 请求参数校验（@Valid + JSR-303）
- [ ] 编写 Service 层代码：
  - PointsAccountService：账户 CRUD、积分操作原子性
  - PointsTransactionService：流水记录、幂等处理
  - PointsFreezeService：冻结/解冻/过期释放
- [ ] 积分操作业务规则：
  - 积分获取：增加 total_points 和 available_points，记录 EARN 流水
  - 积分消费：扣减 available_points，记录 CONSUME 流水，余额不足时抛异常
  - 积分冻结：从 available_points 转入 frozen_points，创建冻结记录
  - 积分解冻：从 frozen_points 转回 available_points，更新冻结记录状态
  - 冻结积分扣减：扣减 frozen_points 和 total_points，更新冻结记录为 DEDUCTED
- [ ] 并发安全：所有积分变更使用乐观锁（version 字段），失败重试最多 3 次
- [ ] 幂等保证：通过 biz_id 去重，已处理的请求直接返回成功
- [ ] 代码符合 Clean Code 原则，每个 Service 方法有明确的职责边界

---

## 阶段4：质量审计

### 验收标准
- [ ] 输出 `QA/test_report.md`，记录审查结果
- [ ] 安全审查：
  - 无 SQL 注入风险（MyBatis-Plus 参数化查询）
  - 并发测试：同一账户并发扣减积分，最终余额正确
  - 幂等测试：相同 biz_id 重复请求，不会重复入账
  - 冻结过期释放逻辑正确性
- [ ] 性能审查：
  - 积分明细查询使用索引覆盖，避免全表扫描
  - 高频积分查询使用 Redis 缓存热点账户
  - 批量积分操作需在事务内完成，避免长事务锁表
- [ ] 单元测试覆盖：
  - PointsAccountService 的 earn/consume/freeze/unfreeze 方法
  - PointsFreezeService 的冻结过期释放逻辑
  - 幂等性：相同 biz_id 重复调用验证
- [ ] 集成测试覆盖：
  - 完整积分获取→消费→查询链路
  - 完整冻结→解冻→扣减链路
  - 并发冲突场景（多线程同时操作同一账户）
- [ ] 代码覆盖率 ≥ 80%

---

## 输出物清单

| 阶段 | 输出文件 | 负责 Agent |
|------|----------|-----------|
| 架构设计 | `docs/architecture.md`, `docs/db_schema.sql` | 架构与数据编排 |
| 接口契约 | `docs/api_contract.json`, `docs/mcp_schema.md` | 接口契约 |
| 业务实现 | Controller/Service 源码 | 业务逻辑组装 |
| 质量审计 | `QA/test_report.md`, 测试文件 | 稳定性与质量 |

## 技术栈
- 后端框架：Spring Boot 3.x
- 数据库：MySQL 8.0
- 缓存：Redis
- ORM：MyBatis-Plus 或 JPA
- JDK：17+
- 测试框架：JUnit 5 + Mockito + Testcontainers
