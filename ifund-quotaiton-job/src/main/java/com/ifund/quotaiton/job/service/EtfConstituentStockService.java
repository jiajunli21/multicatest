package com.ifund.quotaiton.job.service;

import com.ifund.quotaiton.job.dto.EtfConstituentStockRequest;
import com.ifund.quotaiton.job.dto.EtfConstituentStockResponse;
import com.ifund.quotaiton.job.dto.EtfConstituentStockResponse.ConstituentStockItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Service for querying ETF constituent stocks via external dataapi.
 * Contract: DI-006, AD-006. Reference: query code table section 3.
 * Filters constituent stocks to markets 17/33/177 only.
 */
@Service
public class EtfConstituentStockService {

    private static final Logger log = LoggerFactory.getLogger(EtfConstituentStockService.class);

    private final RestTemplate restTemplate;

    @Value("${external.constituent-stock.url}")
    private String constituentStockUrl;

    @Value("${market.codes}")
    private String marketCodes;

    public EtfConstituentStockService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Query constituent stocks for given ETF stock codes.
     * Filters to markets 17/33/177 only.
     *
     * @param etfStockCodes ETF stock codes to query constituent stocks for
     * @return Map of ETF stockCode -> list of constituent stocks
     */
    public Map<String, List<ConstituentStockItem>> fetchConstituentStocks(List<String> etfStockCodes) {
        if (etfStockCodes == null || etfStockCodes.isEmpty()) {
            return Collections.emptyMap();
        }

        try {
            EtfConstituentStockRequest request = new EtfConstituentStockRequest();
            request.setStockCodes(etfStockCodes);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<EtfConstituentStockRequest> entity = new HttpEntity<>(request, headers);

            EtfConstituentStockResponse response = restTemplate.postForObject(
                    constituentStockUrl, entity, EtfConstituentStockResponse.class);

            if (response != null && response.getCode() != null && response.getCode() == 0 && response.getData() != null) {
                Set<String> allowedMarkets = new HashSet<>(Arrays.asList(marketCodes.split(",")));

                // Filter to markets 17/33/177 and group by parent ETF stockCode
                Map<String, List<ConstituentStockItem>> grouped = response.getData().stream()
                        .filter(item -> item.getMarketCode() != null
                                && allowedMarkets.contains(item.getMarketCode().trim()))
                        .collect(Collectors.groupingBy(
                                ConstituentStockItem::getStockCode,
                                Collectors.toList()));

                log.info("Constituent stocks fetched for {} ETFs, filtered to markets {}",
                        grouped.size(), marketCodes);
                return grouped;
            } else {
                log.warn("Constituent stock query returned error: code={}",
                        response != null ? response.getCode() : null);
                return Collections.emptyMap();
            }
        } catch (Exception e) {
            log.error("Constituent stock query failed: {}", e.getMessage(), e);
            return Collections.emptyMap();
        }
    }
}
