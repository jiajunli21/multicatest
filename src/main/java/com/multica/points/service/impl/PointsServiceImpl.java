package com.multica.points.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.multica.points.dto.request.AcquirePointsRequest;
import com.multica.points.dto.request.ConsumePointsRequest;
import com.multica.points.dto.request.FreezePointsRequest;
import com.multica.points.dto.response.FreezeResponse;
import com.multica.points.dto.response.PointsBalanceResponse;
import com.multica.points.dto.response.PointsTransactionResponse;
import com.multica.points.entity.PointsAccount;
import com.multica.points.entity.PointsFreeze;
import com.multica.points.entity.PointsTransaction;
import com.multica.points.exception.InsufficientPointsException;
import com.multica.points.exception.PointsException;
import com.multica.points.mapper.PointsAccountMapper;
import com.multica.points.mapper.PointsFreezeMapper;
import com.multica.points.mapper.PointsTransactionMapper;
import com.multica.points.service.PointsService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class PointsServiceImpl implements PointsService {

    private static final int MAX_RETRY = 3;
    private static final String TX_TYPE_ACQUIRE = "ACQUIRE";
    private static final String TX_TYPE_CONSUME = "CONSUME";
    private static final String TX_TYPE_FREEZE = "FREEZE";
    private static final String TX_TYPE_UNFREEZE = "UNFREEZE";
    private static final String FREEZE_STATUS_FROZEN = "FROZEN";
    private static final String FREEZE_STATUS_RELEASED = "RELEASED";

    private final PointsAccountMapper accountMapper;
    private final PointsTransactionMapper transactionMapper;
    private final PointsFreezeMapper freezeMapper;

    @Override
    @Transactional
    public PointsTransactionResponse acquire(AcquirePointsRequest request) {
        PointsAccount account = getOrCreateAccount(request.getUserId());

        int updated = accountMapper.addBalance(request.getUserId(), request.getAmount(), account.getVersion());
        if (updated == 0) {
            throw new PointsException("VERSION_CONFLICT", "Concurrent modification detected, please retry");
        }

        PointsTransaction tx = buildTransaction(request.getUserId(), TX_TYPE_ACQUIRE, request.getAmount(),
                account.getBalance(), account.getBalance().add(request.getAmount()),
                request.getSource(), request.getSourceId(), request.getDescription());
        transactionMapper.insert(tx);

        log.info("Acquired {} points for user {}, txId={}", request.getAmount(), request.getUserId(), tx.getId());
        return toTransactionResponse(tx);
    }

    @Override
    @Transactional
    public PointsTransactionResponse consume(ConsumePointsRequest request) {
        for (int i = 0; i < MAX_RETRY; i++) {
            PointsAccount account = accountMapper.selectByUserId(request.getUserId());
            if (account == null) {
                throw new InsufficientPointsException(request.getUserId());
            }

            int updated = accountMapper.deductBalance(request.getUserId(), request.getAmount(), account.getVersion());
            if (updated == 0) {
                if (account.getBalance().compareTo(request.getAmount()) < 0) {
                    throw new InsufficientPointsException(request.getUserId());
                }
                log.warn("Version conflict on consume for user {}, retry {}/{}", request.getUserId(), i + 1, MAX_RETRY);
                continue;
            }

            PointsTransaction tx = buildTransaction(request.getUserId(), TX_TYPE_CONSUME, request.getAmount().negate(),
                    account.getBalance(), account.getBalance().subtract(request.getAmount()),
                    request.getSource(), request.getSourceId(), request.getDescription());
            transactionMapper.insert(tx);

            log.info("Consumed {} points for user {}, txId={}", request.getAmount(), request.getUserId(), tx.getId());
            return toTransactionResponse(tx);
        }
        throw new PointsException("VERSION_CONFLICT", "Failed to deduct after " + MAX_RETRY + " retries");
    }

    @Override
    @Transactional
    public FreezeResponse freeze(FreezePointsRequest request) {
        PointsAccount account = getOrCreateAccount(request.getUserId());

        if (account.getBalance().compareTo(request.getAmount()) < 0) {
            throw new InsufficientPointsException(request.getUserId());
        }
        if (request.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new PointsException("INVALID_AMOUNT", "Freeze amount must be positive");
        }

        PointsFreeze freeze = new PointsFreeze();
        freeze.setUserId(request.getUserId());
        freeze.setAmount(request.getAmount());
        freeze.setStatus(FREEZE_STATUS_FROZEN);
        freeze.setReason(request.getReason());
        freeze.setBizId(request.getBizId());
        freezeMapper.insert(freeze);

        log.info("Frozen {} points for user {}, freezeId={}", request.getAmount(), request.getUserId(), freeze.getId());
        return toFreezeResponse(freeze);
    }

    @Override
    @Transactional
    public PointsTransactionResponse unfreeze(Long freezeId) {
        PointsFreeze freeze = freezeMapper.selectById(freezeId);
        if (freeze == null) {
            throw new PointsException("FREEZE_NOT_FOUND", "Freeze record not found: " + freezeId);
        }
        if (!FREEZE_STATUS_FROZEN.equals(freeze.getStatus())) {
            throw new PointsException("FREEZE_STATUS_INVALID",
                    "Freeze record is not in FROZEN status, current: " + freeze.getStatus());
        }

        int updated = freezeMapper.updateStatus(freezeId, FREEZE_STATUS_RELEASED, FREEZE_STATUS_FROZEN);
        if (updated == 0) {
            throw new PointsException("FREEZE_STATUS_CONFLICT", "Freeze status was modified concurrently");
        }

        PointsAccount account = accountMapper.selectByUserId(freeze.getUserId());
        PointsTransaction tx = buildTransaction(freeze.getUserId(), TX_TYPE_UNFREEZE, freeze.getAmount(),
                account.getBalance(), account.getBalance().add(freeze.getAmount()),
                "UNFREEZE", String.valueOf(freezeId),
                "Unfreeze from record #" + freezeId + ": " + freeze.getReason());
        transactionMapper.insert(tx);

        log.info("Unfrozen {} points for user {}, freezeId={}", freeze.getAmount(), freeze.getUserId(), freezeId);
        return toTransactionResponse(tx);
    }

    @Override
    public PointsBalanceResponse getBalance(String userId) {
        PointsAccount account = accountMapper.selectByUserId(userId);
        BigDecimal balance = account != null ? account.getBalance() : BigDecimal.ZERO;
        BigDecimal frozenBalance = freezeMapper.sumFrozenAmount(userId);

        return PointsBalanceResponse.builder()
                .userId(userId)
                .balance(balance)
                .frozenBalance(frozenBalance)
                .availableBalance(balance.subtract(frozenBalance))
                .totalEarned(account != null ? account.getTotalEarned() : BigDecimal.ZERO)
                .totalSpent(account != null ? account.getTotalSpent() : BigDecimal.ZERO)
                .build();
    }

    @Override
    public List<PointsTransactionResponse> getTransactions(String userId, int page, int size) {
        LambdaQueryWrapper<PointsTransaction> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(PointsTransaction::getUserId, userId)
                .orderByDesc(PointsTransaction::getCreatedAt);

        Page<PointsTransaction> result = transactionMapper.selectPage(new Page<>(page, size), wrapper);
        return result.getRecords().stream()
                .map(this::toTransactionResponse)
                .collect(Collectors.toList());
    }

    @Override
    public List<FreezeResponse> getFreezeRecords(String userId) {
        LambdaQueryWrapper<PointsFreeze> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(PointsFreeze::getUserId, userId)
                .orderByDesc(PointsFreeze::getCreatedAt);

        return freezeMapper.selectList(wrapper).stream()
                .map(this::toFreezeResponse)
                .collect(Collectors.toList());
    }

    private PointsAccount getOrCreateAccount(String userId) {
        PointsAccount account = accountMapper.selectByUserId(userId);
        if (account == null) {
            account = new PointsAccount();
            account.setUserId(userId);
            account.setBalance(BigDecimal.ZERO);
            account.setTotalEarned(BigDecimal.ZERO);
            account.setTotalSpent(BigDecimal.ZERO);
            accountMapper.insert(account);
            account = accountMapper.selectByUserId(userId);
        }
        return account;
    }

    private PointsTransaction buildTransaction(String userId, String txType, BigDecimal amount,
                                                BigDecimal balanceBefore, BigDecimal balanceAfter,
                                                String source, String sourceId, String description) {
        PointsTransaction tx = new PointsTransaction();
        tx.setUserId(userId);
        tx.setTxType(txType);
        tx.setAmount(amount);
        tx.setBalanceBefore(balanceBefore);
        tx.setBalanceAfter(balanceAfter);
        tx.setSource(source);
        tx.setSourceId(sourceId);
        tx.setDescription(description);
        return tx;
    }

    private PointsTransactionResponse toTransactionResponse(PointsTransaction tx) {
        return PointsTransactionResponse.builder()
                .id(tx.getId())
                .userId(tx.getUserId())
                .txType(tx.getTxType())
                .amount(tx.getAmount())
                .balanceBefore(tx.getBalanceBefore())
                .balanceAfter(tx.getBalanceAfter())
                .source(tx.getSource())
                .description(tx.getDescription())
                .createdAt(tx.getCreatedAt())
                .build();
    }

    private FreezeResponse toFreezeResponse(PointsFreeze freeze) {
        return FreezeResponse.builder()
                .freezeId(freeze.getId())
                .userId(freeze.getUserId())
                .amount(freeze.getAmount())
                .status(freeze.getStatus())
                .reason(freeze.getReason())
                .createdAt(freeze.getCreatedAt())
                .build();
    }
}
