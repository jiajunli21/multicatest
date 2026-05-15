-- Todo 任务管理系统 —— 数据库 Schema
-- 目标数据库：SQLite（开发期）
-- 迁移工具：Drizzle ORM / drizzle-kit

-- 任务表
CREATE TABLE IF NOT EXISTS todos (
    id          TEXT PRIMARY KEY,                -- UUID v4，服务端通过 crypto.randomUUID() 生成
    title       TEXT NOT NULL,                    -- 任务标题，1-200 字符，应用层校验
    description TEXT,                             -- 任务描述，可为 NULL，最大 2000 字符，应用层校验
    status      TEXT NOT NULL DEFAULT 'todo',     -- 状态枚举：todo | in_progress | done
    created_at  TEXT NOT NULL,                    -- 创建时间，ISO 8601 UTC 格式
    updated_at  TEXT NOT NULL                     -- 最后更新时间，ISO 8601 UTC 格式
);

-- 按状态过滤查询索引
CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);

-- 按创建时间倒序排列索引（列表查询主排序）
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at DESC);
