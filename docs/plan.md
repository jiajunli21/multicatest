# Todo 任务管理系统 —— 阶段计划文档

## 需求目标

构建一个 Todo 任务管理系统后端服务，提供 RESTful API 支持任务的创建、查询、状态更新与删除。系统以单体后端服务形态交付，为前端或 API 消费者提供完整的任务管理能力。

## 功能范围

| 功能 | 说明 |
|------|------|
| 创建任务 | 接受任务标题与可选描述，生成唯一任务 ID，初始状态为 `todo` |
| 查询任务列表 | 支持分页查询，可选按状态过滤，按创建时间倒序排列 |
| 查询任务详情 | 根据任务 ID 返回单个任务的完整信息 |
| 更新任务状态 | 支持将任务状态在 `todo` -> `in_progress` -> `done` 之间流转 |
| 删除任务 | 根据任务 ID 软删除或硬删除任务 |

## 非目标

- 用户认证与授权（单用户系统，无需登录）
- 任务分配与多人协作
- 任务优先级、标签、分类
- 任务截止日期与提醒
- 任务评论与附件
- 数据持久化以外的存储方案（不做 Redis 缓存等）
- 前端 UI 界面（仅提供 API）
- WebSocket 实时推送

## 核心业务流程

### 1. 任务创建流程

```
客户端 -> POST /api/todos {title, description?}
       -> 校验 title 非空
       -> 生成 UUID
       -> 设置 status = "todo"
       -> 记录 created_at, updated_at
       -> 持久化存储
       -> 返回 201 + 完整任务对象
```

### 2. 任务列表查询流程

```
客户端 -> GET /api/todos?status={status}&page={page}&page_size={page_size}
       -> 默认 page=1, page_size=20, 最大 page_size=100
       -> 可选按 status 过滤
       -> 按 created_at DESC 排序
       -> 返回 {items: [...], total: N, page: N, page_size: N}
```

### 3. 任务详情查询流程

```
客户端 -> GET /api/todos/{id}
       -> 按 ID 查找
       -> 存在则返回 200 + 任务对象
       -> 不存在则返回 404
```

### 4. 任务状态更新流程

```
客户端 -> PATCH /api/todos/{id}/status {status: "in_progress"|"done"}
       -> 按 ID 查找
       -> 不存在则返回 404
       -> 校验状态流转合法性：
            todo -> in_progress (允许)
            todo -> done (允许，跳过中间态)
            in_progress -> done (允许)
            in_progress -> todo (允许，回退)
            done -> todo (允许，重新打开)
            done -> in_progress (允许)
       -> 更新 status 与 updated_at
       -> 返回 200 + 更新后任务对象
```

### 5. 任务删除流程

```
客户端 -> DELETE /api/todos/{id}
       -> 按 ID 查找
       -> 不存在则返回 404
       -> 执行删除
       -> 返回 204 No Content
```

## 领域对象

### Task（任务）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string (UUID) | 是 | 任务唯一标识，服务端生成 |
| title | string | 是 | 任务标题，非空，最长 200 字符 |
| description | string | 否 | 任务描述，最长 2000 字符 |
| status | enum | 是 | `todo` / `in_progress` / `done`，默认 `todo` |
| created_at | datetime | 是 | 创建时间，服务端生成 |
| updated_at | datetime | 是 | 最后更新时间，服务端生成 |

### Status 状态枚举

```
todo ──────> in_progress ──────> done
  │                                    │
  └────────────> done                  │
  ^                                    │
  └────────────────────────────────────┘
```

任何状态之间允许直接转换（不做严格状态机限制），以降低使用复杂度。未来如需严格流转控制，可在 Service 层加入状态机校验。

## 前后端任务拆分建议

### 后端（本次交付范围）

- 数据层：定义 Task Schema / 模型
- 持久层：实现 CRUD 操作（内存或 SQLite 均可）
- 服务层：实现业务逻辑与校验
- 接口层：实现 RESTful API Controller
- 测试：Service 单元测试 + API 集成测试

### 前端（本次不做，预留对接点）

- API 基础路径：`/api/todos`
- 请求/响应格式：JSON
- 需处理的标准 HTTP 状态码：200, 201, 204, 400, 404, 500

### 建议技术栈（供下游架构阶段决策）

| 层 | 可选方案 | 推荐 |
|----|----------|------|
| 语言/框架 | Go/Gin, Python/Flask, Node/Express, TypeScript/Hono | 由架构阶段决定 |
| 存储 | SQLite, PostgreSQL, MySQL, 内存 | 开发期可用 SQLite |
| ORM | GORM, Prisma, SQLAlchemy | 由架构阶段决定 |

## 测试关注点

### Service 层单元测试

- 创建任务：title 为空应返回校验错误
- 创建任务：正常输入应返回完整 Task 对象
- 查询列表：空列表返回空 items
- 查询列表：分页边界（page=0, page_size=0, page_size>100）
- 查询列表：状态过滤正确性
- 查询详情：不存在的 ID 返回错误
- 更新状态：不存在的 ID 返回错误
- 更新状态：无效状态值返回校验错误
- 删除任务：不存在的 ID 返回错误
- 删除任务：删除后再次查询应返回不存在

### API 层集成测试

- 各端点 HTTP 状态码正确性
- 请求体 JSON 格式校验
- 响应体结构与字段完整性
- 分页参数默认值与上限

## 风险与边界情况

| 风险/边界 | 说明 | 建议处理 |
|-----------|------|----------|
| title 为空 | 无标题的任务无意义 | 返回 400 + 明确错误信息 |
| title 超长 | 恶意长标题 | 限制 200 字符，超出返回 400 |
| description 超长 | 大量文本 | 限制 2000 字符 |
| 并发更新 | 两个请求同时更新同一任务状态 | 当前版本不做乐观锁，以最后写入为准；后续可加 version 字段 |
| ID 不存在 | 操作不存在的任务 | 统一返回 404 |
| SQL 注入 | 使用字符串拼接查询 | 必须使用参数化查询或 ORM |
| 分页过大 | page_size 极大值 | 限制最大 100 |
| 数据丢失 | 内存存储重启丢失 | 下游需明确持久化方案（SQLite 最低要求） |
| 删除方式 | 硬删除 vs 软删除 | 建议硬删除（简单）；如需审计可加软删除（增加 deleted_at 字段） |
