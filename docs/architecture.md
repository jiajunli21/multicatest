# Todo 任务管理系统 —— 架构文档

## 概述

本文档定义 Todo 任务管理系统的整体架构、模块划分、数据流、存储模型和关键设计决策，供下游接口契约（WS-4）和业务实现（WS-5）直接使用。

## 技术选型

| 层 | 选型 | 理由 |
|----|------|------|
| 语言 | TypeScript | 类型安全，与 JSON API 天然契合 |
| 运行时 | Node.js (>=18) | LTS 稳定，生态丰富 |
| 框架 | Hono | 轻量、高性能、原生 TypeScript 支持 |
| ORM | Drizzle ORM | TypeScript-first、SQL-like API、轻量无代码生成 |
| 数据库 | SQLite (开发期) | 零配置、文件级持久化，后续可平滑迁移到 PostgreSQL |
| UUID 生成 | `crypto.randomUUID()` | Node.js 内置，无额外依赖 |

### 选型约束

- **SQLite 仅用于开发期**：生产环境建议 PostgreSQL，Drizzle ORM 支持无缝切换
- **不使用内存存储**：SQLite 提供文件级持久化，避免重启丢失数据
- **不引入 Redis / 消息队列**：单用户系统无需缓存和异步解耦

## 模块划分

```
src/
├── index.ts             # 入口：创建 Hono 实例，注册路由
├── db/
│   ├── schema.ts        # Drizzle ORM Schema 定义（表结构）
│   ├── index.ts         # 数据库连接初始化
│   └── migrate.ts       # 迁移执行
├── repository/
│   └── todo.repository.ts   # 数据访问层：封装所有 SQL 操作
├── service/
│   └── todo.service.ts      # 业务逻辑层：校验、状态流转、编排
├── handler/
│   └── todo.handler.ts      # HTTP 处理层：请求解析、响应构造
├── router/
│   └── todo.router.ts       # 路由注册：绑定路径与方法
└── types/
    └── todo.ts              # 共享类型定义（Task, CreateTodoInput, etc.）
```

### 模块职责与边界

| 模块 | 职责 | 依赖 | 不负责 |
|------|------|------|--------|
| `types/` | 定义 Task 类型、DTO 接口、状态枚举 | 无 | 不包含任何运行时逻辑 |
| `db/schema.ts` | 定义表结构和字段约束 | `drizzle-orm` | 不包含业务校验 |
| `db/index.ts` | 初始化数据库连接 | `schema.ts` | 不暴露连接细节给上层 |
| `repository/` | 执行 CRUD SQL，返回 Drizzle 查询结果 | `db/` | 不做业务校验，不处理 HTTP |
| `service/` | 输入校验、状态流转规则、业务错误 | `repository/`, `types/` | 不接触 HTTP 请求/响应 |
| `handler/` | 解析请求参数、调用 service、构造 HTTP 响应 | `service/`, `types/` | 不包含业务逻辑 |
| `router/` | 注册路由路径和 HTTP 方法 | `handler/` | 不处理请求体 |

### 分层原则

```
HTTP Request
    │
    ▼
router/          ← 路由匹配
    │
    ▼
handler/         ← 请求解析、参数提取、响应构造
    │
    ▼
service/         ← 业务校验、状态流转、错误定义
    │
    ▼
repository/      ← SQL 执行、分页计算
    │
    ▼
db/schema.ts     ← 表定义、字段约束
```

- **上层可调用下层，下层不可反向依赖上层**
- **每层只暴露接口，隐藏实现细节**
- **跨层的数据传递使用 `types/` 中的共享类型**

## 核心数据流

### 创建任务

```
POST /api/todos {title, description?}
  → handler: 解析 JSON body，提取 title/description
  → service.createTodo(input):
      1. 校验 title 非空、长度 ≤ 200
      2. 校验 description（若提供）长度 ≤ 2000
      3. 生成 UUID (crypto.randomUUID())
      4. 设置 status = "todo"
      5. 设置 created_at = updated_at = now
      6. 调用 repository.insert(task)
  → repository: INSERT INTO todos ... RETURNING *
  → handler: 返回 201 + Task 对象
```

### 查询任务列表

```
GET /api/todos?status={status}&page={page}&page_size={page_size}
  → handler: 解析 query params
      1. page 默认 1，最小 1
      2. page_size 默认 20，最小 1，最大 100
      3. status 可选，校验是否为有效状态值
  → service.listTodos(filter):
      1. 校验 status（若提供）
      2. 调用 repository.findMany(filter)
  → repository:
      1. 构建 WHERE 子句（可选 status 过滤）
      2. COUNT(*) 获取总数
      3. SELECT ... ORDER BY created_at DESC LIMIT ? OFFSET ?
  → handler: 返回 200 + {items, total, page, page_size}
```

### 查询任务详情

```
GET /api/todos/{id}
  → handler: 提取路径参数 id
  → service.getTodo(id):
      1. 调用 repository.findById(id)
      2. 不存在则抛出 NotFoundError
  → repository: SELECT ... WHERE id = ?
  → handler: 存在返回 200，不存在返回 404
```

### 更新任务状态

```
PATCH /api/todos/{id}/status {status: "todo"|"in_progress"|"done"}
  → handler: 提取路径参数 id，解析 JSON body
  → service.updateStatus(id, status):
      1. 校验 status 是否为有效枚举值
      2. 调用 repository.findById(id)
      3. 不存在则抛出 NotFoundError
      4. 状态流转不做限制（任意状态间可转换）
      5. 更新 status, updated_at = now
      6. 调用 repository.update(id, patch)
  → repository: UPDATE todos SET status=?, updated_at=? WHERE id=?
  → handler: 返回 200 + 更新后 Task 对象
```

### 删除任务

```
DELETE /api/todos/{id}
  → handler: 提取路径参数 id
  → service.deleteTodo(id):
      1. 调用 repository.findById(id)
      2. 不存在则抛出 NotFoundError
      3. 调用 repository.delete(id)
  → repository: DELETE FROM todos WHERE id = ?
  → handler: 返回 204 No Content
```

## 领域模型

### Task 实体

| 字段 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| id | string (UUID v4) | 是 | 服务端生成 | PRIMARY KEY | 任务唯一标识 |
| title | string | 是 | - | NOT NULL, 长度 1-200 | 任务标题 |
| description | string | 否 | null | 长度 0-2000 | 任务描述，允许为空 |
| status | enum | 是 | `"todo"` | NOT NULL, 枚举值 `todo`/`in_progress`/`done` | 任务状态 |
| created_at | datetime | 是 | 服务端生成 | NOT NULL | 创建时间 (ISO 8601 UTC) |
| updated_at | datetime | 是 | 服务端生成 | NOT NULL | 最后更新时间 (ISO 8601 UTC) |

### Status 枚举

```
todo ──────> in_progress ──────> done
  │                                    │
  └────────────> done                  │
  ^                                    │
  └────────────────────────────────────┘
  ^                                    │
  └──── 任意两个状态之间可直接转换 ─────┘
```

**设计决策：不做严格状态机限制。** 理由见上游决策——降低使用复杂度，任意 `todo` / `in_progress` / `done` 之间均可直接转换。

### 输入 DTO

```typescript
// 创建任务输入
interface CreateTodoInput {
  title: string;          // 必填，1-200 字符
  description?: string;   // 可选，最大 2000 字符
}

// 更新状态输入
interface UpdateStatusInput {
  status: "todo" | "in_progress" | "done";
}

// 列表查询参数
interface ListTodosQuery {
  status?: "todo" | "in_progress" | "done";
  page?: number;       // 默认 1
  page_size?: number;  // 默认 20，最大 100
}
```

### 响应结构

```typescript
// 单个任务响应
interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  status: "todo" | "in_progress" | "done";
  created_at: string;  // ISO 8601
  updated_at: string;  // ISO 8601
}

// 列表响应
interface ListTodosResponse {
  items: TaskResponse[];
  total: number;
  page: number;
  page_size: number;
}

// 错误响应
interface ErrorResponse {
  error: string;
  message: string;
}
```

## 数据存储结构

### 数据库：SQLite

- **数据库文件**：`data/todos.db`（仓库根目录下 `data/` 目录，已加入 `.gitignore`）
- **连接方式**：单文件，通过 Drizzle ORM 的 `better-sqlite3` 驱动连接
- **迁移策略**：使用 `drizzle-kit` 生成 SQL 迁移文件，存放在 `drizzle/` 目录

### 表结构

```sql
CREATE TABLE todos (
    id          TEXT PRIMARY KEY,                -- UUID v4
    title       TEXT NOT NULL,                    -- 1-200 chars
    description TEXT,                             -- nullable, max 2000 chars
    status      TEXT NOT NULL DEFAULT 'todo',     -- 'todo' | 'in_progress' | 'done'
    created_at  TEXT NOT NULL,                    -- ISO 8601 UTC
    updated_at  TEXT NOT NULL                     -- ISO 8601 UTC
);

CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_created_at ON todos(created_at DESC);
```

### 索引策略

| 索引 | 字段 | 用途 |
|------|------|------|
| `idx_todos_status` | `status` | 按状态过滤列表查询 |
| `idx_todos_created_at` | `created_at DESC` | 列表排序（高频查询） |

### 删除策略

**硬删除**：`DELETE FROM todos WHERE id = ?`，数据从数据库物理删除，不可恢复。这是上游明确决策——简单直接，无需 `deleted_at` 字段和软删除逻辑。

## 查询与写入边界

### 查询边界

| 操作 | SQL 模式 | 备注 |
|------|----------|------|
| 按 ID 查询 | `SELECT * FROM todos WHERE id = ?` | 主键查询，O(1) |
| 列表查询（无过滤） | `SELECT * FROM todos ORDER BY created_at DESC LIMIT ? OFFSET ?` | 使用 `created_at` 索引 |
| 列表查询（按状态过滤） | `SELECT * FROM todos WHERE status = ? ORDER BY created_at DESC LIMIT ? OFFSET ?` | 使用 `status` 索引 + `created_at` 索引 |
| 计数 | `SELECT COUNT(*) FROM todos [WHERE status = ?]` | 分页 total 计算 |

### 写入边界

| 操作 | SQL 模式 | 备注 |
|------|----------|------|
| 创建 | `INSERT INTO todos (...) VALUES (...)` | 单行插入 |
| 更新状态 | `UPDATE todos SET status = ?, updated_at = ? WHERE id = ?` | 只更新 status 和 updated_at |
| 删除 | `DELETE FROM todos WHERE id = ?` | 硬删除 |

### 分页约定

- **默认 page_size**：20
- **最大 page_size**：100
- **page 从 1 开始**：page < 1 时视为 1
- **OFFSET 计算**：`(page - 1) * page_size`
- **total 返回总记录数**（受 status 过滤影响）

## 一致性与并发风险

### 当前策略：最后写入胜出（Last-Write-Wins）

单用户系统，并发写入概率极低。当前版本不做乐观锁、不做事务隔离级别调优。两个请求同时更新同一任务状态时，以后到达的请求为准。

### 已知风险

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 并发更新覆盖 | 两个请求同时更新同一任务，后者覆盖前者的 status | 单用户场景可接受；后续可加 `version` 字段做乐观锁 |
| 读-改-写竞态 | 读取 status 后基于旧值决定新值 | 当前状态流转无前置条件，竞态无实际影响 |
| 删除后立即创建（同 ID） | 不存在此场景（UUID 由服务端生成，不会复用） | 无需处理 |
| SQLite 写锁 | SQLite 单写锁，并发写入会串行化 | 单用户场景下不是问题 |

### 后续升级路径

如需支持多用户或更高并发：
1. 添加 `version` 整型字段，更新时 `WHERE id = ? AND version = ?`，版本冲突返回 409
2. 切换到 PostgreSQL，利用行级锁和更强的事务隔离
3. 对状态字段引入状态机校验（限制合法转换路径）

## 错误处理约定

| 场景 | HTTP 状态码 | error | message 示例 |
|------|-------------|-------|-------------|
| title 为空 | 400 | `VALIDATION_ERROR` | `Title is required` |
| title 超长 | 400 | `VALIDATION_ERROR` | `Title must be at most 200 characters` |
| description 超长 | 400 | `VALIDATION_ERROR` | `Description must be at most 2000 characters` |
| 无效状态值 | 400 | `VALIDATION_ERROR` | `Invalid status: "archived". Must be todo, in_progress, or done` |
| 无效 status 过滤值 | 400 | `VALIDATION_ERROR` | `Invalid status filter: "xxx"` |
| page_size 超限 | 400 | `VALIDATION_ERROR` | `page_size must be at most 100` |
| 任务不存在 | 404 | `NOT_FOUND` | `Todo with id "xxx" not found` |
| JSON 解析失败 | 400 | `INVALID_JSON` | `Invalid JSON in request body` |
| 未知错误 | 500 | `INTERNAL_ERROR` | `An unexpected error occurred` |

## 后续接口契约需要覆盖的对象和动作

### 端点清单

| 方法 | 路径 | 说明 | Handler |
|------|------|------|---------|
| POST | `/api/todos` | 创建任务 | `createTodo` |
| GET | `/api/todos` | 查询任务列表 | `listTodos` |
| GET | `/api/todos/:id` | 查询任务详情 | `getTodo` |
| PATCH | `/api/todos/:id/status` | 更新任务状态 | `updateTodoStatus` |
| DELETE | `/api/todos/:id` | 删除任务 | `deleteTodo` |

### 请求/响应对象

| 对象 | 用途 | 字段 |
|------|------|------|
| `CreateTodoRequest` | POST body | `title` (required), `description` (optional) |
| `UpdateStatusRequest` | PATCH body | `status` (required, enum) |
| `ListTodosQuery` | GET query params | `status`, `page`, `page_size` |
| `TaskResponse` | 所有成功响应中的任务对象 | `id`, `title`, `description`, `status`, `created_at`, `updated_at` |
| `ListTodosResponse` | GET /api/todos 响应 | `items`, `total`, `page`, `page_size` |
| `ErrorResponse` | 所有错误响应 | `error`, `message` |

### 下游阶段的输入约束

1. **API 契约（WS-4）** 必须基于本文档的端点清单、请求/响应对象和错误处理约定生成
2. **业务实现（WS-5）** 必须遵循本文档的模块划分和分层原则
3. **数据库 Schema** 使用 `schema/todos.sql`，不可偏离表结构定义
4. **状态枚举** 严格限定为 `todo` / `in_progress` / `done`，不可新增
