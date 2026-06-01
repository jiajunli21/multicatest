package com.ifund.quotaiton.job.service;

import com.ifund.quotaiton.job.dto.EtfFuyaoRequest;
import com.ifund.quotaiton.job.dto.EtfFuyaoResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for querying real-time market data via Fuyou (扶摇) system.
 * Contract: DI-002, DI-003, DI-004, DI-007.
 * Reference: query code table sections 2/4/5/6.
 *
 * Soft blocker: Fuyao URL is empty, request body structure follows query code table.
 */
@Service
public class EtfFuyaoService {

    private static final Logger log = LoggerFactory.getLogger(EtfFuyaoService.class);

    private final RestTemplate restTemplate;

    @Value("${external.fuyao.url}")
    private String fuyaoUrl;

    @Value("${market.codes}")
    private String marketCodes;

    @Value("${market.all-stocks-page-size}")
    private int allStocksPageSize;

    public EtfFuyaoService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Query ETF price_change_ratio_pct (涨幅) via Fuyou. SNAPSHOT timetype.
     * Contract: DI-002, AD-002. Reference: query code table section 2.
     */
    public Map<String, BigDecimal> queryEtfChangeRatio(List<String> stockCodes) {
        if (stockCodes == null || stockCodes.isEmpty()) {
            return Collections.emptyMap();
        }
        return queryField(stockCodes, "price_change_ratio_pct", "SNAPSHOT");
    }

    /**
     * Query ETF price_change_speed_ratio_pct (涨速) via Fuyou. SNAPSHOT timetype.
     * Contract: DI-003, AD-003. Reference: query code table section 5.
     */
    public Map<String, BigDecimal> queryEtfSpeedRatio(List<String> stockCodes) {
        if (stockCodes == null || stockCodes.isEmpty()) {
            return Collections.emptyMap();
        }
        return queryField(stockCodes, "price_change_speed_ratio_pct", "SNAPSHOT");
    }

    /**
     * Query ETF volume ratio (量比) via Fuyou. NOW timetype.
     * Contract: DI-004, AD-004. Reference: query code table section 6.
     */
    public Map<String, BigDecimal> queryEtfVolumeRatio(List<String> stockCodes) {
        if (stockCodes == null || stockCodes.isEmpty()) {
            return Collections.emptyMap();
        }
        return queryField(stockCodes, "hq-fncdict-1771976", "NOW");
    }

    /**
     * Query all-market stock price_change_ratio_pct for constituent stock intersection.
     * Markets: 17 (SH), 33 (SZ), 177 (BJ). SNAPSHOT timetype.
     * Contract: DI-007, AD-007. Reference: query code table section 4.
     * Soft blocker: page_size defaults to 100000.
     */
    public Map<String, BigDecimal> queryAllMarketStockChangeRatio() {
        try {
            String[] markets = marketCodes.split(",");
            Map<String, BigDecimal> result = new HashMap<>();

            for (String market : markets) {
                Map<String, Object> codeSelector = new HashMap<>();
                codeSelector.put("market_code", market.trim());

                EtfFuyaoRequest request = buildRequest(
                        Collections.singletonList(codeSelector),
                        Collections.singletonList("price_change_ratio_pct"),
                        "SNAPSHOT",
                        allStocksPageSize
                );

                Map<String, BigDecimal> marketResult = executeQuery(request);
                result.putAll(marketResult);
                log.info("Market {} returned {} stock change ratios", market, marketResult.size());
            }

            return result;
        } catch (Exception e) {
            log.error("All-market stock change ratio query failed: {}", e.getMessage(), e);
            return Collections.emptyMap();
        }
    }

    /**
     * Generic Fuyou field query.
     */
    private Map<String, BigDecimal> queryField(List<String> stockCodes, String indexId, String timetype) {
        try {
            List<Map<String, Object>> codeSelectors = stockCodes.stream()
                    .map(code -> {
                        Map<String, Object> selector = new HashMap<>();
                        selector.put("stock_code", code);
                        return selector;
                    })
                    .collect(Collectors.toList());

            EtfFuyaoRequest request = buildRequest(codeSelectors,
                    Collections.singletonList(indexId), timetype, stockCodes.size());

            return executeQuery(request);
        } catch (Exception e) {
            log.error("Fuyou query failed for indexId={}: {}", indexId, e.getMessage(), e);
            return Collections.emptyMap();
        }
    }

    private EtfFuyaoRequest buildRequest(List<Map<String, Object>> codeSelectors,
                                          List<String> indexes,
                                          String timetype,
                                          int pageSize) {
        EtfFuyaoRequest request = new EtfFuyaoRequest();
        request.setCodeSelectors(codeSelectors);
        request.setIndexes(indexes);

        EtfFuyaoRequest.PageInfo pageInfo = new EtfFuyaoRequest.PageInfo();
        pageInfo.setPageSize(pageSize);
        pageInfo.setPageNum(1);
        request.setPageInfo(pageInfo);

        return request;
    }

    private Map<String, BigDecimal> executeQuery(EtfFuyaoRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<EtfFuyaoRequest> entity = new HttpEntity<>(request, headers);

        EtfFuyaoResponse response = restTemplate.postForObject(
                fuyaoUrl, entity, EtfFuyaoResponse.class);

        Map<String, BigDecimal> result = new HashMap<>();
        if (response != null && response.getCode() != null && response.getCode() == 0 && response.getData() != null) {
            String indexId = request.getIndexes().get(0);
            for (Map<String, Object> row : response.getData()) {
                String stockCode = EtfFuyaoResponse.getString(row, "stock_code");
                BigDecimal value = EtfFuyaoResponse.getBigDecimal(row, indexId);
                if (stockCode != null && value != null) {
                    result.put(stockCode, value);
                }
            }
        } else {
            log.warn("Fuyou query returned error or empty: code={}",
                    response != null ? response.getCode() : null);
        }
        return result;
    }
}
