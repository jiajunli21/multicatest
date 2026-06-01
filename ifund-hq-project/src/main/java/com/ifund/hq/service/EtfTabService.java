package com.ifund.hq.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ifund.hq.dto.EtfRankData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class EtfTabService {

    private static final Logger log = LoggerFactory.getLogger(EtfTabService.class);

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    @Value("${etf-tab.redis.key:plateStatEtf:rank:data}")
    private String redisKey;

    @Value("${etf-tab.cache.name:etfRankData}")
    private String cacheName;

    public EtfTabService(StringRedisTemplate redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    @Cacheable(value = "etfRankData", key = "'rankData'", unless = "#result == null")
    public EtfRankData getEtfRankData() {
        log.debug("Caffeine miss, reading from Redis key: {}", redisKey);
        try {
            String json = redisTemplate.opsForValue().get(redisKey);
            if (json != null && !json.isEmpty()) {
                EtfRankData data = objectMapper.readValue(json, EtfRankData.class);
                log.debug("Redis hit, calcDate={}, calcTimestamp={}", data.getCalcDate(), data.getCalcTimestamp());
                return data;
            }
        } catch (Exception e) {
            log.warn("Failed to read or parse Redis key {}: {}", redisKey, e.getMessage());
        }
        log.debug("Redis miss, returning empty EtfRankData");
        return null;
    }

    public EtfRankData getEmptyRankData() {
        return new EtfRankData();
    }
}
