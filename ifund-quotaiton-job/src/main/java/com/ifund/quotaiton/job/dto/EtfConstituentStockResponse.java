package com.ifund.quotaiton.job.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.List;

/**
 * Constituent stock relationship query response.
 * Reference: query code table section 3.
 */
public class EtfConstituentStockResponse {

    @JsonProperty("code")
    private Integer code;

    @JsonProperty("message")
    private String message;

    @JsonProperty("data")
    private List<ConstituentStockItem> data;

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<ConstituentStockItem> getData() {
        return data;
    }

    public void setData(List<ConstituentStockItem> data) {
        this.data = data;
    }

    /**
     * A single constituent stock entry.
     */
    public static class ConstituentStockItem {

        /** ETF stock code (parent) */
        @JsonProperty("stockCode")
        private String stockCode;

        /** Constituent stock code */
        @JsonProperty("code")
        private String code;

        /** Constituent stock name */
        @JsonProperty("name")
        private String name;

        /** Market code: 17/33/177 */
        @JsonProperty("marketCode")
        private String marketCode;

        /** Holding ratio */
        @JsonProperty("etfSecurityHoldrate")
        private BigDecimal etfSecurityHoldrate;

        public String getStockCode() {
            return stockCode;
        }

        public void setStockCode(String stockCode) {
            this.stockCode = stockCode;
        }

        public String getCode() {
            return code;
        }

        public void setCode(String code) {
            this.code = code;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getMarketCode() {
            return marketCode;
        }

        public void setMarketCode(String marketCode) {
            this.marketCode = marketCode;
        }

        public BigDecimal getEtfSecurityHoldrate() {
            return etfSecurityHoldrate;
        }

        public void setEtfSecurityHoldrate(BigDecimal etfSecurityHoldrate) {
            this.etfSecurityHoldrate = etfSecurityHoldrate;
        }
    }
}
