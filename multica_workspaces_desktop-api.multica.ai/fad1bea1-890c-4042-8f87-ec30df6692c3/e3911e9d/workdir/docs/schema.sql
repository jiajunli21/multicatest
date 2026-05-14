-- 用户积分系统 — 数据库 Schema
-- 阶段：BEW-3（架构与数据编排）
-- 目标数据库：MySQL 8.0+ / InnoDB
-- 金额单位：分（INT/BIGINT），无浮点数，避免精度丢失

-- ============================================================
-- 1. 积分账户表
-- ============================================================
CREATE TABLE point_accounts (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT  COMMENT '自增主键',
    user_id         VARCHAR(64)     NOT NULL                 COMMENT '用户 ID，外部系统标识',
    available_balance BIGINT       NOT NULL DEFAULT 0       COMMENT '可用积分余额（分）',
    frozen_balance  BIGINT          NOT NULL DEFAULT 0       COMMENT '冻结积分余额（分）',
    total_earned    BIGINT          NOT NULL DEFAULT 0       COMMENT '累计获取积分（只增不减）',
    total_spent     BIGINT          NOT NULL DEFAULT 0       COMMENT '累计消费积分（只增不减）',
    version         INT UNSIGNED    NOT NULL DEFAULT 0       COMMENT '乐观锁版本号',
    created_at      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    updated_at      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',

    PRIMARY KEY (id),
    UNIQUE KEY uk_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='积分账户';

-- ============================================================
-- 2. 积分明细表
-- ============================================================
CREATE TABLE point_transactions (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT  COMMENT '自增主键',
    user_id         VARCHAR(64)     NOT NULL                 COMMENT '用户 ID',
    type            ENUM('EARN','SPEND','FREEZE','UNFREEZE','DEDUCT') NOT NULL COMMENT '变动类型',
    amount          BIGINT          NOT NULL                 COMMENT '变动金额（分，正数）',
    balance_after   BIGINT          NOT NULL                 COMMENT '变动后可用余额（分）',
    frozen_after    BIGINT          NOT NULL DEFAULT 0       COMMENT '变动后冻结余额（分）',
    remaining       BIGINT          NOT NULL DEFAULT 0       COMMENT '剩余可用额度（分，仅 EARN 类型维护，用于 FIFO 扣减追踪）',
    source          VARCHAR(64)     NOT NULL DEFAULT ''      COMMENT '来源渠道标识（如 activity/task/admin）',
    reference_id    VARCHAR(128)    NOT NULL                 COMMENT '关联业务单号（幂等键）',
    expires_at      DATETIME(3)     DEFAULT NULL             COMMENT '过期时间（仅 EARN 类型有效，NULL = 永不过期）',
    metadata        JSON            DEFAULT NULL             COMMENT '扩展信息',
    created_at      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',

    PRIMARY KEY (id),
    UNIQUE KEY uk_idempotent (user_id, type, reference_id),
    INDEX idx_user_created (user_id, created_at DESC),
    INDEX idx_user_type_created (user_id, type, created_at DESC),
    INDEX idx_earn_remaining (user_id, expires_at, remaining)  -- FIFO 消费查询：按用户 + 过期时间排序
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='积分明细';

-- ============================================================
-- 3. 冻结记录表
-- ============================================================
CREATE TABLE freeze_records (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT  COMMENT '自增主键',
    user_id         VARCHAR(64)     NOT NULL                 COMMENT '用户 ID',
    amount          BIGINT          NOT NULL                 COMMENT '初始冻结金额（分）',
    remaining       BIGINT          NOT NULL                 COMMENT '剩余冻结金额（分，解冻/扣减后递减）',
    reason          VARCHAR(256)    NOT NULL DEFAULT ''      COMMENT '冻结原因',
    operator_id     VARCHAR(64)     NOT NULL                 COMMENT '操作人 ID',
    status          ENUM('ACTIVE','RELEASED','DEDUCTED') NOT NULL DEFAULT 'ACTIVE' COMMENT '冻结状态',
    reference_id    VARCHAR(128)    NOT NULL                 COMMENT '关联业务单号',
    metadata        JSON            DEFAULT NULL             COMMENT '扩展信息',
    version         INT UNSIGNED    NOT NULL DEFAULT 0       COMMENT '乐观锁版本号',
    created_at      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    updated_at      DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',

    PRIMARY KEY (id),
    INDEX idx_user_status (user_id, status),
    INDEX idx_user_created (user_id, created_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  COMMENT='冻结记录';
