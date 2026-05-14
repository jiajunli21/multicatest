package com.multica.points.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("points_account")
public class PointsAccount {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String userId;

    private BigDecimal balance;

    private BigDecimal totalEarned;

    private BigDecimal totalSpent;

    @Version
    private Integer version;

    @TableLogic
    private Integer deleted;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
}
