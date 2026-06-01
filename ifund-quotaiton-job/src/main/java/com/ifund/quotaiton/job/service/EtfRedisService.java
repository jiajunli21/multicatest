package com.ifund.quotaiton.job.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ifund.quotaiton.job.dto.EtfRankData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * Redis operations for ETF ranking data.
 * Contract: DI-011, AD-009.
 *
 * Write mode: Overwrite JSON to key plateStatEtf:rank:data with TTL 2 minutes (SBLK-002).
 * Distributed lock: Redis SETNX (SBLK-003).
 */
@Service
public class EtfRedisService {

    private static final Logger log = LoggerFactory.getLogger(EtfRedisService.class);

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    @Value("${block-stat-etf-tab.redis.key}")
    private String rankDataKey;

    @Value("${block-stat-etf-tab.redis.ttl-seconds}")
    private long ttlSeconds;

    @Value("${block-stat-etf-tab.redis.lock-key}")
    private String lockKey;

    @Value("${block-stat-etf-tab.redis.lock-ttl-seconds}")
    private long lockTtlSeconds;

    public EtfRedisService(StringRedisTemplate redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Acquire distributed lock via SETNX to prevent concurrent execution.
     */
    public boolean tryLock() {
        Boolean success = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, "1", lockTtlSeconds, TimeUnit.SECONDS);
        return Boolean.TRUE.equals(success);
    }

    /**
     * Release distributed lock.
     */
    public void unlock() {
        redisTemplate.delete(lockKey);
    }

    /**
     * Write ETF rank data to Redis as JSON.
     * Overwrites existing value, sets TTL.
     */
    public void writeRankData(EtfRankData rankData) {
        try {
            String json = objectMapper.writeValueAsString(rankData);
            redisTemplate.opsForValue().set(rankDataKey, json, ttlSeconds, TimeUnit.SECONDS);
            log.info("Wrote ETF rank data to Redis key={}, ttl={}s, jsonSize={}",
                    rankDataKey, ttlSeconds, json.length());
        } catch (Exception e) {
            log.error("Failed to write ETF rank data to Redis: {}", e.getMessage(), e);
        }
    }

    /**
     * Read ETF rank data from Redis (for verification/testing).
     */
    public EtfRankData readRankData() {
        try {
            String json = redisTemplate.opsForValue().get(rankDataKey);
            if (json != null && !json.isEmpty()) {
                return objectMapper.readValue(json, EtfRankData.class);
            }
        } catch (Exception e) {
            log.error("Failed to read ETF rank data from Redis: {}", e.getMessage(), e);
        }
        return null;
    }

    public String getRankDataKey() {
        return rankDataKey;
    }

    public long getTtlSeconds() {
        return ttlSeconds;
    }
}
