package com.multica.points.service;

import com.multica.points.dto.request.AcquirePointsRequest;
import com.multica.points.dto.request.ConsumePointsRequest;
import com.multica.points.dto.request.FreezePointsRequest;
import com.multica.points.dto.response.FreezeResponse;
import com.multica.points.dto.response.PointsBalanceResponse;
import com.multica.points.dto.response.PointsTransactionResponse;

import java.util.List;

public interface PointsService {

    PointsTransactionResponse acquire(AcquirePointsRequest request);

    PointsTransactionResponse consume(ConsumePointsRequest request);

    FreezeResponse freeze(FreezePointsRequest request);

    PointsTransactionResponse unfreeze(Long freezeId);

    PointsBalanceResponse getBalance(String userId);

    List<PointsTransactionResponse> getTransactions(String userId, int page, int size);

    List<FreezeResponse> getFreezeRecords(String userId);
}
