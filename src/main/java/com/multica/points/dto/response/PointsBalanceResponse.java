package com.multica.points.dto.response;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;

@Data
@Builder
public class PointsBalanceResponse {

    private String userId;
    private BigDecimal balance;
    private BigDecimal frozenBalance;
    private BigDecimal availableBalance;
    private BigDecimal totalEarned;
    private BigDecimal totalSpent;
}
