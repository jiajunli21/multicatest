-- 用户积分系统 — 数据库 Schema
-- 产出阶段：BEW-3（架构与数据编排）
-- 目标数据库：PostgreSQL 14+
-- 生成时间：2026-05-14

-- ============================================================
-- 枚举类型
-- ============================================================

-- 积分变动类型
DO $$ BEGIN
    CREATE TYPE point_txn_type AS ENUM ('EARN', 'SPEND', 'FREEZE', 'UNFREEZE', 'DEDUCT');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- 冻结记录状态
DO $$ BEGIN
    CREATE TYPE freeze_status AS ENUM ('ACTIVE', 'RELEASED', 'DEDUCTED');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- 表定义
-- ============================================================

-- 积分账户表
-- 与 user_id 一一对应，首次 EARN 时 lazy create
CREATE TABLE IF NOT EXISTS point_accounts (
    id                UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           VARCHAR(64)     NOT NULL,
    available_balance BIGINT          NOT NULL DEFAULT 0  CHECK (available_balance >= 0),
    frozen_balance    BIGINT          NOT NULL DEFAULT 0  CHECK (frozen_balance >= 0),
    total_earned      BIGINT          NOT NULL DEFAULT 0  CHECK (total_earned >= 0),
    total_spent       BIGINT          NOT NULL DEFAULT 0  CHECK (total_spent >= 0),
    version           INTEGER         NOT NULL DEFAULT 1,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- 唯一约束：一个用户仅一个积分账户
CREATE UNIQUE INDEX IF NOT EXISTS idx_point_accounts_user_id
    ON point_accounts (user_id);

-- ============================================================

-- 积分明细表（只追加，不修改不删除）
CREATE TABLE IF NOT EXISTS point_transactions (
    id                UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           VARCHAR(64)     NOT NULL,
    type              point_txn_type  NOT NULL,
    amount            BIGINT          NOT NULL CHECK (amount > 0),
    balance_after     BIGINT          NOT NULL,
    frozen_after      BIGINT          NOT NULL,
    source            VARCHAR(64)     NOT NULL DEFAULT '',
    reference_id      VARCHAR(128)    NOT NULL,
    expires_at        TIMESTAMPTZ,
    metadata          JSONB           NOT NULL DEFAULT '{}',
    freeze_record_id  UUID,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- 幂等控制：同一用户 + 同一类型 + 同一业务单号 不可重复
CREATE UNIQUE INDEX IF NOT EXISTS idx_point_txn_idempotent
    ON point_transactions (user_id, type, reference_id);

-- 明细列表分页查询：按用户 + 时间倒序
CREATE INDEX IF NOT EXISTS idx_point_txn_user_time
    ON point_transactions (user_id, created_at DESC);

-- 即将过期积分查询（外部调度器使用）
CREATE INDEX IF NOT EXISTS idx_point_txn_expires
    ON point_transactions (expires_at)
    WHERE type = 'EARN' AND expires_at IS NOT NULL;

-- ============================================================

-- 冻结记录表
CREATE TABLE IF NOT EXISTS freeze_records (
    id                UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           VARCHAR(64)     NOT NULL,
    amount            BIGINT          NOT NULL CHECK (amount > 0),
    remaining         BIGINT          NOT NULL CHECK (remaining >= 0),
    reason            VARCHAR(256)    NOT NULL DEFAULT '',
    operator_id       VARCHAR(64)     NOT NULL,
    status            freeze_status   NOT NULL DEFAULT 'ACTIVE',
    metadata          JSONB           NOT NULL DEFAULT '{}',
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- 按用户查询活跃冻结记录
CREATE INDEX IF NOT EXISTS idx_freeze_records_user_status
    ON freeze_records (user_id, status);

-- 管理后台按状态和时间查询
CREATE INDEX IF NOT EXISTS idx_freeze_records_status_time
    ON freeze_records (status, created_at DESC);

-- ============================================================
-- 外键约束（冻结记录 → 明细关联）
-- ============================================================

DO $$ BEGIN
    ALTER TABLE point_transactions
        ADD CONSTRAINT fk_point_txn_freeze_record
        FOREIGN KEY (freeze_record_id) REFERENCES freeze_records (id);
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================
-- 示例查询（供 BEW-4 / BEW-5 参考）
-- ============================================================

-- Lazy create 账户（首次 EARN 时）
-- INSERT INTO point_accounts (user_id, available_balance, total_earned)
-- VALUES (:user_id, :amount, :amount)
-- ON CONFLICT (user_id) DO NOTHING;

-- 带乐观锁的余额更新
-- UPDATE point_accounts
-- SET available_balance = available_balance + :delta,
--     frozen_balance = frozen_balance + :frozen_delta,
--     total_earned = total_earned + :earned_delta,
--     total_spent = total_spent + :spent_delta,
--     version = version + 1,
--     updated_at = NOW()
-- WHERE user_id = :user_id AND version = :old_version
-- RETURNING version, available_balance, frozen_balance;

-- 查询即将过期的积分（未过期的 EARN 记录，按过期时间排序）
-- SELECT id, user_id, amount, expires_at
-- FROM point_transactions
-- WHERE type = 'EARN' AND expires_at IS NOT NULL AND expires_at <= NOW() + INTERVAL '7 days'
-- ORDER BY expires_at ASC;

-- 用户余额查询
-- SELECT available_balance, frozen_balance
-- FROM point_accounts
-- WHERE user_id = :user_id;

-- 用户明细分页查询
-- SELECT id, type, amount, balance_after, frozen_after, source, reference_id, expires_at, created_at
-- FROM point_transactions
-- WHERE user_id = :user_id
--   AND (:type IS NULL OR type = :type)
--   AND (:since IS NULL OR created_at >= :since)
--   AND (:until IS NULL OR created_at <= :until)
-- ORDER BY created_at DESC
-- LIMIT :page_size OFFSET :offset;
