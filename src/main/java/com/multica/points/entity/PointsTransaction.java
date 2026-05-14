package com.multica.points.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("points_transaction")
public class PointsTransaction {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String userId;

    @TableField("tx_type")
    private String txType;

    private BigDecimal amount;

    private BigDecimal balanceBefore;

    private BigDecimal balanceAfter;

    private String source;

    private String sourceId;

    private String description;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
