# Quality Review — Todo 任务管理系统 (WS-6)

**审查日期**: 2026-05-15
**审查范围**: WS-5 产物（handler / service / repository / types / db schema）
**上游基准**: commit `77df215`，docs/api_contract.json，docs/architecture.md

## 审查结论

**有条件通过** — 核心逻辑正确，已修复 1 个 bug 并补充测试覆盖。下游可基于当前分支继续工作。

## 审查范围

| 模块 | 文件 | 审查点 |
|------|------|--------|
| handler | `src/handler/todo.handler.ts` | 请求解析、参数校验、错误处理、HTTP 状态码 |
| service | `src/service/todo.service.ts` | 业务校验、状态流转、错误抛出、分页逻辑 |
| repository | `src/repository/todo.repository.ts` | SQL 正确性、分页计算、索引利用 |
| types | `src/types/todo.ts` | 类型定义完整性、错误类层次 |
| db schema | `src/db/schema.ts` | 表结构与架构文档一致性 |
| router | `src/router/todo.router.ts` | 路由与 API 契约一致性 |
| api contract | `docs/api_contract.json` | 作为校验基准 |
| architecture | `docs/architecture.md` | 作为设计基准 |

## 发现项

### Bug 修复

| # | 严重度 | 描述 | 位置 | 修复 |
|---|--------|------|------|------|
| B1 | 中 | `page_size` 查询参数未做 NaN 校验，与 `page` 不一致。当传入非数字字符串（如 `?page_size=abc`）时，`parseInt` 返回 `NaN`，穿透 handler 和 service 层的分页计算（`Math.max(1, NaN)` = `NaN`），最终传入 Drizzle 的 `.limit(NaN)` / `.offset(NaN)` | `src/handler/todo.handler.ts:28` (原) | 新增 `page_size` 的 NaN 和范围校验，与 `page` 保持一致；同时 service 层增加防御性 NaN 保护 |

### 正面发现

| # | 评价 | 说明 |
|---|------|------|
| P1 | 分层清晰 | handler → service → repository 职责分离严格，与 `docs/architecture.md` 定义一致 |
| P2 | 错误模型完整 | `AppError` → `ValidationError` / `NotFoundError` 继承层次合理，`handleError` 集中处理 |
| P3 | API 契约一致 | 5 个端点路由路径、HTTP 方法、请求/响应格式与 `docs/api_contract.json` 完全匹配 |
| P4 | 状态枚举约束 | `VALID_STATUSES` 常量驱动校验，避免魔法字符串，易于扩展 |
| P5 | 分页稳健 | 多层防御（handler 默认值 → service 边界 clamp → repository offset 计算），默认值合理 |
| P6 | 输入清理 | title/description 做 trim 处理，防止空白字符串绕过非空校验 |
| P7 | 删除前存在性校验 | `deleteTodo` 在删除前先查存在性，保证 404 语义正确 |
| P8 | SQLite WAL 模式 | `db/index.ts` 启用 WAL，提升并发读性能 |
| P9 | 索引策略 | `status` 和 `created_at` 索引覆盖列表查询的场景（按状态过滤 + 时间排序） |

### 代码质量观察（非阻塞）

| # | 严重度 | 描述 | 建议 |
|---|--------|------|------|
| O1 | 低 | 分页计算逻辑在 service 和 repository 两层重复（`Math.max(1, ...)` / `Math.min(100, ...)`） | 考虑将分页 clamp 收敛到 repository，service 只做语义校验 |
| O2 | 低 | `handler/listTodos` 使用 `as any` 类型断言绕过 TypeScript 检查 | 可定义精确的输入类型替代 `as any` |
| O3 | 低 | `repo.deleteById` 返回值未被 service 使用 | 当前无影响（存在性已前置校验），后续如需审计日志可考虑利用 |

## 测试覆盖

新增测试文件：

| 文件 | 测试数 | 覆盖范围 |
|------|--------|----------|
| `tests/service/todo.service.test.ts` | 28 | createTodo 校验 (10), listTodos 分页/过滤 (8), getTodo (2), updateStatus (5), deleteTodo (2) |
| `tests/handler/todo.handler.test.ts` | 21 | POST 创建 (4), GET 列表 (7), GET 详情 (2), PATCH 状态更新 (3), DELETE 删除 (3) |
| **合计** | **49** | 全部 49 个测试通过 |

### 覆盖明细

**Service 层（单元测试，mock repository）**:
- `createTodo`: 正常创建、无描述、title trim、空 title、空白 title、title 超长、title 边界 (200)、description 超长、description 边界 (2000)、description trim、默认 status、UUID 唯一性
- `listTodos`: 默认分页、status 过滤、无效 status 报错、page_size > 100 报错、page_size 边界、page clamp、NaN page_size 防御、NaN page 防御、响应映射
- `getTodo`: 正常查找、不存在的 ID
- `updateStatus`: 正常更新、无效 status 报错、不存在的任务、全部三种有效 status、done→todo 逆向转换
- `deleteTodo`: 正常删除、不存在的任务

**Handler 层（集成测试，mock service）**:
- `POST /api/todos`: 201 正常创建、400 参数校验、400 非法 JSON、500 内部错误
- `GET /api/todos`: 200 正常列表、query params 透传、非法 page 纠正、非法 page_size 纠正、0 page 纠正、0 page_size 纠正、400 service 报错
- `GET /api/todos/:id`: 200 详情、404 不存在
- `PATCH /api/todos/:id/status`: 200 更新、400 非法 JSON、404 不存在
- `DELETE /api/todos/:id`: 204 正常删除、404 不存在、500 内部错误

## 与 API 契约一致性检查

| 端点 | 契约定义 | 实现 | 一致 |
|------|----------|------|------|
| `POST /api/todos` | 201 / 400 / 500 | ✓ | ✓ |
| `GET /api/todos` | 200 (items, total, page, page_size) | ✓ | ✓ |
| `GET /api/todos/{id}` | 200 / 404 / 500 | ✓ | ✓ |
| `PATCH /api/todos/{id}/status` | 200 / 400 / 404 / 500 | ✓ | ✓ |
| `DELETE /api/todos/{id}` | 204 / 404 / 500 | ✓ | ✓ |

所有端点响应格式与 `docs/api_contract.json` 中定义的 `ErrorResponse` 结构一致：`{"error": "<code>", "message": "<description>"}`。

## 与架构文档一致性检查

| 架构要求 | 实现 | 一致 |
|----------|------|------|
| handler → service → repository 分层 | ✓ | ✓ |
| title 必填 1-200 字符 | ✓ | ✓ |
| description 可选 ≤2000 字符 | ✓ | ✓ |
| status 枚举 todo/in_progress/done | ✓ | ✓ |
| 状态任意转换（无状态机限制） | ✓ | ✓ |
| UUID 由服务端生成 | ✓ | ✓ |
| created_at/updated_at 服务端管理 | ✓ | ✓ |
| 分页默认 page=1 page_size=20 | ✓ | ✓ |
| 列表按 created_at DESC | ✓ | ✓ |
| 硬删除 | ✓ | ✓ |
| DELETE 返回 204 | ✓ | ✓ |

## 稳定性风险评估

| 风险 | 等级 | 说明 |
|------|------|------|
| 并发写入覆盖 | 低 | 架构文档已明确 Last-Write-Wins 策略，单用户场景可接受 |
| SQLite 单写锁 | 低 | 单用户场景无需担心 |
| 无输入 XSS 防护 | 低 | API 返回 JSON，现代前端框架默认转义；title 已有长度限制 |
| 缺少请求速率限制 | 信息 | 未被要求，后续可考虑 |

## 文件清单（本次变更）

```
M  src/handler/todo.handler.ts  — 修复 page_size NaN 校验
M  src/service/todo.service.ts  — 防御性 NaN 保护
M  package.json                 — 新增 test/test:watch 脚本
A  vitest.config.ts             — vitest 配置
A  tests/service/todo.service.test.ts  — service 层单元测试 (28 tests)
A  tests/handler/todo.handler.test.ts  — handler 层集成测试 (21 tests)
A  docs/quality_review.md       — 本文档
```
