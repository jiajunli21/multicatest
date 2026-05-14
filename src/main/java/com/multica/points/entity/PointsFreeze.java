package com.multica.points.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("points_freeze")
public class PointsFreeze {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String userId;

    private BigDecimal amount;

    private String status;

    private String reason;

    private String bizId;

    private LocalDateTime expiredAt;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
}
