package com.ifund.quotaiton.job.service;

import com.ifund.quotaiton.job.dto.EtfFundPoolResponse;
import com.ifund.quotaiton.job.dto.EtfFundPoolResponse.EtfFundPoolItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

/**
 * Service for querying the fund pool API to get industry-themed ETF lists.
 * Contract: DI-001, AD-001. Reference: query code table section 1.
 */
@Service
public class EtfFundPoolService {

    private static final Logger log = LoggerFactory.getLogger(EtfFundPoolService.class);

    private final RestTemplate restTemplate;

    @Value("${external.fund-pool.url}")
    private String fundPoolUrl;

    @Value("${external.fund-pool.unique-type}")
    private String uniqueType;

    public EtfFundPoolService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    /**
     * Fetch industry-themed ETF list from fund pool.
     * @return ETF list, empty list on failure
     */
    public List<EtfFundPoolItem> fetchIndustryThemeEtfs() {
        try {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("uniqueType", uniqueType);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            EtfFundPoolResponse response = restTemplate.postForObject(
                    fundPoolUrl, entity, EtfFundPoolResponse.class);

            if (response != null && response.getCode() != null && response.getCode() == 0 && response.getData() != null) {
                log.info("Fund pool returned {} ETFs for uniqueType={}", response.getData().size(), uniqueType);
                return response.getData();
            } else {
                log.warn("Fund pool returned error: code={}, msg={}",
                        response != null ? response.getCode() : null,
                        response != null ? response.getMessage() : null);
                return Collections.emptyList();
            }
        } catch (Exception e) {
            log.error("Fund pool query failed: {}", e.getMessage(), e);
            return Collections.emptyList();
        }
    }
}
