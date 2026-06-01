package com.ifund.hq.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ifund.hq.dto.EtfRankData;
import com.ifund.hq.dto.EtfRankItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;

@Service
public class EtfTabService {

    private static final Logger log = LoggerFactory.getLogger(EtfTabService.class);

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;

    @Value("${etf-tab.redis.key}")
    private String rankDataKey;

    public EtfTabService(StringRedisTemplate redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    @Cacheable(value = "etfRankData", key = "'rank'")
    public EtfRankData getRankData() {
        String json = redisTemplate.opsForValue().get(rankDataKey);
        if (json != null && !json.isEmpty()) {
            try {
                log.info("Caffeine miss, loaded from Redis key={}", rankDataKey);
                return objectMapper.readValue(json, EtfRankData.class);
            } catch (JsonProcessingException e) {
                log.error("Failed to deserialize Redis data: {}", e.getMessage());
            }
        }
        log.warn("Both Caffeine and Redis miss, returning empty rank structure");
        return emptyRankData();
    }

    public EtfRankData filterByRankType(EtfRankData full, String rankType) {
        EtfRankData filtered = emptyRankData();
        filtered.setCalcTimestamp(full.getCalcTimestamp());
        filtered.setCalcDate(full.getCalcDate());
        switch (rankType) {
            case "changeRatio":
                filtered.setChangeRatioTop9(full.getChangeRatioTop9());
                filtered.setChangeRatioBottom9(full.getChangeRatioBottom9());
                break;
            case "speedRatio":
                filtered.setSpeedRatioTop9(full.getSpeedRatioTop9());
                filtered.setSpeedRatioBottom9(full.getSpeedRatioBottom9());
                break;
            case "volumeRatio":
                filtered.setVolumeRatioTop9(full.getVolumeRatioTop9());
                filtered.setVolumeRatioBottom9(full.getVolumeRatioBottom9());
                break;
            case "limitUpCount":
                filtered.setLimitUpCountTop9(full.getLimitUpCountTop9());
                filtered.setLimitUpCountBottom9(full.getLimitUpCountBottom9());
                break;
            default:
                break;
        }
        return filtered;
    }

    private EtfRankData emptyRankData() {
        EtfRankData empty = new EtfRankData();
        List<EtfRankItem> emptyList = Collections.emptyList();
        empty.setChangeRatioTop9(emptyList);
        empty.setChangeRatioBottom9(emptyList);
        empty.setSpeedRatioTop9(emptyList);
        empty.setSpeedRatioBottom9(emptyList);
        empty.setVolumeRatioTop9(emptyList);
        empty.setVolumeRatioBottom9(emptyList);
        empty.setLimitUpCountTop9(emptyList);
        empty.setLimitUpCountBottom9(emptyList);
        return empty;
    }
}
