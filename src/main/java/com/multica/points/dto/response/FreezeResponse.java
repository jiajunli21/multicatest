package com.multica.points.dto.response;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
public class FreezeResponse {

    private Long freezeId;
    private String userId;
    private BigDecimal amount;
    private String status;
    private String reason;
    private LocalDateTime createdAt;
}
