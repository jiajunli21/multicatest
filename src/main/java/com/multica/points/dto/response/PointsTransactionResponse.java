package com.multica.points.dto.response;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
public class PointsTransactionResponse {

    private Long id;
    private String userId;
    private String txType;
    private BigDecimal amount;
    private BigDecimal balanceBefore;
    private BigDecimal balanceAfter;
    private String source;
    private String description;
    private LocalDateTime createdAt;
}
