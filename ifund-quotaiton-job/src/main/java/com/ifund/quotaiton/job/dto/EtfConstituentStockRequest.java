package com.ifund.quotaiton.job.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * Constituent stock relationship query request.
 * Reference: query code table section 3.
 */
public class EtfConstituentStockRequest {

    @JsonProperty("stock_codes")
    private List<String> stockCodes;

    public List<String> getStockCodes() {
        return stockCodes;
    }

    public void setStockCodes(List<String> stockCodes) {
        this.stockCodes = stockCodes;
    }
}
