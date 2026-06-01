package com.ifund.hq.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;

public class EtfRankItem {

    @JsonProperty("stockCode")
    private String stockCode;

    @JsonProperty("marketCode")
    private String marketCode;

    @JsonProperty("name")
    private String name;

    @JsonProperty("tradeCode")
    private String tradeCode;

    @JsonProperty("rankType")
    private String rankType;

    @JsonProperty("rankValue")
    private BigDecimal rankValue;

    @JsonProperty("rank")
    private Integer rank;

    @JsonProperty("rankOrder")
    private String rankOrder;

    @JsonProperty("topLeadStockCode")
    private String topLeadStockCode;

    @JsonProperty("topLeadStockName")
    private String topLeadStockName;

    @JsonProperty("topLeadStockChangeRatio")
    private BigDecimal topLeadStockChangeRatio;

    @JsonProperty("topLeadStockHoldRate")
    private BigDecimal topLeadStockHoldRate;

    @JsonProperty("bottomLeadStockCode")
    private String bottomLeadStockCode;

    @JsonProperty("bottomLeadStockName")
    private String bottomLeadStockName;

    @JsonProperty("bottomLeadStockChangeRatio")
    private BigDecimal bottomLeadStockChangeRatio;

    @JsonProperty("bottomLeadStockHoldRate")
    private BigDecimal bottomLeadStockHoldRate;

    public String getStockCode() {
        return stockCode;
    }

    public void setStockCode(String stockCode) {
        this.stockCode = stockCode;
    }

    public String getMarketCode() {
        return marketCode;
    }

    public void setMarketCode(String marketCode) {
        this.marketCode = marketCode;
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

    public String getRankType() {
        return rankType;
    }

    public void setRankType(String rankType) {
        this.rankType = rankType;
    }

    public BigDecimal getRankValue() {
        return rankValue;
    }

    public void setRankValue(BigDecimal rankValue) {
        this.rankValue = rankValue;
    }

    public Integer getRank() {
        return rank;
    }

    public void setRank(Integer rank) {
        this.rank = rank;
    }

    public String getRankOrder() {
        return rankOrder;
    }

    public void setRankOrder(String rankOrder) {
        this.rankOrder = rankOrder;
    }

    public String getTopLeadStockCode() {
        return topLeadStockCode;
    }

    public void setTopLeadStockCode(String topLeadStockCode) {
        this.topLeadStockCode = topLeadStockCode;
    }

    public String getTopLeadStockName() {
        return topLeadStockName;
    }

    public void setTopLeadStockName(String topLeadStockName) {
        this.topLeadStockName = topLeadStockName;
    }

    public BigDecimal getTopLeadStockChangeRatio() {
        return topLeadStockChangeRatio;
    }

    public void setTopLeadStockChangeRatio(BigDecimal topLeadStockChangeRatio) {
        this.topLeadStockChangeRatio = topLeadStockChangeRatio;
    }

    public BigDecimal getTopLeadStockHoldRate() {
        return topLeadStockHoldRate;
    }

    public void setTopLeadStockHoldRate(BigDecimal topLeadStockHoldRate) {
        this.topLeadStockHoldRate = topLeadStockHoldRate;
    }

    public String getBottomLeadStockCode() {
        return bottomLeadStockCode;
    }

    public void setBottomLeadStockCode(String bottomLeadStockCode) {
        this.bottomLeadStockCode = bottomLeadStockCode;
    }

    public String getBottomLeadStockName() {
        return bottomLeadStockName;
    }

    public void setBottomLeadStockName(String bottomLeadStockName) {
        this.bottomLeadStockName = bottomLeadStockName;
    }

    public BigDecimal getBottomLeadStockChangeRatio() {
        return bottomLeadStockChangeRatio;
    }

    public void setBottomLeadStockChangeRatio(BigDecimal bottomLeadStockChangeRatio) {
        this.bottomLeadStockChangeRatio = bottomLeadStockChangeRatio;
    }

    public BigDecimal getBottomLeadStockHoldRate() {
        return bottomLeadStockHoldRate;
    }

    public void setBottomLeadStockHoldRate(BigDecimal bottomLeadStockHoldRate) {
        this.bottomLeadStockHoldRate = bottomLeadStockHoldRate;
    }
}
