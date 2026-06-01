package com.ifund.hq.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

@Configuration
@EnableCaching
public class EtfCacheConfig {

    @Value("${etf-tab.cache.name:etfRankData}")
    private String cacheName;

    @Value("${etf-tab.cache.ttl-seconds:30}")
    private long ttlSeconds;

    @Value("${etf-tab.cache.max-size:100}")
    private int maxSize;

    @Bean
    public CacheManager etfCacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager(cacheName);
        cacheManager.setCaffeine(Caffeine.newBuilder()
                .expireAfterWrite(ttlSeconds, TimeUnit.SECONDS)
                .maximumSize(maxSize)
                .recordStats());
        cacheManager.setAllowNullValues(false);
        return cacheManager;
    }
}
