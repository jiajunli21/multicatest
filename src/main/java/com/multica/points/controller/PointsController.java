package com.multica.points.controller;

import com.multica.points.dto.request.AcquirePointsRequest;
import com.multica.points.dto.request.ConsumePointsRequest;
import com.multica.points.dto.request.FreezePointsRequest;
import com.multica.points.dto.response.FreezeResponse;
import com.multica.points.dto.response.PointsBalanceResponse;
import com.multica.points.dto.response.PointsTransactionResponse;
import com.multica.points.service.PointsService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/points")
@RequiredArgsConstructor
@Validated
public class PointsController {

    private final PointsService pointsService;

    @PostMapping("/acquire")
    @ResponseStatus(HttpStatus.CREATED)
    public PointsTransactionResponse acquire(@Valid @RequestBody AcquirePointsRequest request) {
        return pointsService.acquire(request);
    }

    @PostMapping("/consume")
    public PointsTransactionResponse consume(@Valid @RequestBody ConsumePointsRequest request) {
        return pointsService.consume(request);
    }

    @PostMapping("/freeze")
    @ResponseStatus(HttpStatus.CREATED)
    public FreezeResponse freeze(@Valid @RequestBody FreezePointsRequest request) {
        return pointsService.freeze(request);
    }

    @PostMapping("/unfreeze/{freezeId}")
    public PointsTransactionResponse unfreeze(@PathVariable Long freezeId) {
        return pointsService.unfreeze(freezeId);
    }

    @GetMapping("/balance/{userId}")
    public PointsBalanceResponse getBalance(@NotBlank @PathVariable String userId) {
        return pointsService.getBalance(userId);
    }

    @GetMapping("/transactions/{userId}")
    public List<PointsTransactionResponse> getTransactions(
            @NotBlank @PathVariable String userId,
            @RequestParam(defaultValue = "1") @Min(1) int page,
            @RequestParam(defaultValue = "20") @Min(1) @Max(100) int size) {
        return pointsService.getTransactions(userId, page, size);
    }

    @GetMapping("/freeze/{userId}")
    public List<FreezeResponse> getFreezeRecords(@NotBlank @PathVariable String userId) {
        return pointsService.getFreezeRecords(userId);
    }
}
