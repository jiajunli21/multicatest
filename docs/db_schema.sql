-- ============================================================
-- 用户积分系统 — 数据库 Schema
-- 目标：MySQL 8.0+ / InnoDB
-- 金额单位：分（整数，避免浮点精度问题）
-- ============================================================

-- ------------------------------------------------------------
-- 1. 用户积分表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_points (
    user_id        VARCHAR(64)  NOT NULL COMMENT '用户唯一标识',
    total_points   BIGINT       NOT NULL DEFAULT 0 COMMENT '总积分（分）',
    frozen_points  BIGINT       NOT NULL DEFAULT 0 COMMENT '冻结积分（分）',
    version        INT          NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
    created_at     DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    updated_at     DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '最后更新时间',
    PRIMARY KEY (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户积分账户表';

-- ------------------------------------------------------------
-- 2. 积分流水表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS points_transaction (
    id              BIGINT       NOT NULL AUTO_INCREMENT COMMENT '流水ID',
    user_id         VARCHAR(64)  NOT NULL COMMENT '用户标识',
    type            ENUM('earn','spend','freeze','unfreeze') NOT NULL COMMENT '操作类型',
    amount          BIGINT       NOT NULL COMMENT '变动金额（分，正数）',
    balance_before  BIGINT       NOT NULL COMMENT '操作前 total_points',
    balance_after   BIGINT       NOT NULL COMMENT '操作后 total_points',
    reference_id    VARCHAR(128) NOT NULL COMMENT '幂等键（业务方生成的唯一标识，如订单号）',
    description     VARCHAR(256) DEFAULT NULL COMMENT '备注说明',
    created_at      DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_reference_id (reference_id) COMMENT '幂等唯一约束',
    INDEX idx_user_created (user_id, created_at DESC) COMMENT '按用户分页查询明细'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分交易流水表（不可变）';

-- ------------------------------------------------------------
-- 3. 冻结记录表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS points_freeze_record (
    id          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '冻结记录ID',
    user_id     VARCHAR(64)  NOT NULL COMMENT '用户标识',
    amount      BIGINT       NOT NULL COMMENT '冻结金额（分）',
    status      ENUM('frozen','unfrozen') NOT NULL DEFAULT 'frozen' COMMENT '状态',
    reason      VARCHAR(256) DEFAULT NULL COMMENT '冻结原因',
    created_at  DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
    unfrozen_at DATETIME(3)  DEFAULT NULL COMMENT '解冻时间',
    PRIMARY KEY (id),
    INDEX idx_user_status (user_id, status) COMMENT '按用户查询活跃冻结'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分冻结记录表';

-- ============================================================
-- 数据一致性校验 SQL（供 QA 阶段使用）
-- ============================================================

-- 校验 1: 冻结积分总额 = 所有未解冻的冻结记录金额之和
-- SELECT
--   u.user_id,
--   u.frozen_points AS account_frozen,
--   COALESCE(SUM(f.amount), 0) AS record_frozen_sum
-- FROM user_points u
-- LEFT JOIN points_freeze_record f ON u.user_id = f.user_id AND f.status = 'frozen'
-- GROUP BY u.user_id
-- HAVING account_frozen != record_frozen_sum;

-- 校验 2: 可用积分不为负
-- SELECT user_id, total_points, frozen_points
-- FROM user_points
-- WHERE total_points < frozen_points;
