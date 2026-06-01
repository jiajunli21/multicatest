package com.ifund.quotaiton.job.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.List;

/**
 * Fund pool query response containing ETF list.
 * Reference: query code table section 1.
 */
public class EtfFundPoolResponse {

    @JsonProperty("code")
    private Integer code;

    @JsonProperty("message")
    private String message;

    @JsonProperty("data")
    private List<EtfFundPoolItem> data;

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

    public List<EtfFundPoolItem> getData() {
        return data;
    }

    public void setData(List<EtfFundPoolItem> data) {
        this.data = data;
    }

    /**
     * A single ETF entry from the fund pool.
     */
    public static class EtfFundPoolItem {

        @JsonProperty("stockCode")
        private String stockCode;

        @JsonProperty("market")
        private String market;

        @JsonProperty("name")
        private String name;

        @JsonProperty("tradeCode")
        private String tradeCode;

        @JsonProperty("etfLimitUpStockCnt")
        private Integer etfLimitUpStockCnt;

        public String getStockCode() {
            return stockCode;
        }

        public void setStockCode(String stockCode) {
            this.stockCode = stockCode;
        }

        public String getMarket() {
            return market;
        }

        public void setMarket(String market) {
            this.market = market;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getTradeCode() {
            return tradeCode;
        }

        public void setTradeCode(String tradeCode) {
            this.tradeCode = tradeCode;
        }

        public Integer getEtfLimitUpStockCnt() {
            return etfLimitUpStockCnt;
        }

        public void setEtfLimitUpStockCnt(Integer etfLimitUpStockCnt) {
            this.etfLimitUpStockCnt = etfLimitUpStockCnt;
        }
    }
}
