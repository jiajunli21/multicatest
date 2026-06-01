package com.ifund.quotaiton.job.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;

/**
 * A single ETF entry in a ranking list.
 * Fields follow query code table section 9 naming conventions.
 */
public class EtfRankItem {

    /** ETF代码 */
    @JsonProperty("stockCode")
    private String stockCode;

    /** 市场代码 17/33/177 */
    @JsonProperty("marketCode")
    private String marketCode;

    /** ETF名称 */
    @JsonProperty("name")
    private String name;

    /** 交易代码（展示用） */
    @JsonProperty("tradeCode")
    private String tradeCode;

    /** 排序类型: changeRatio/speedRatio/volumeRatio/limitUpCount */
    @JsonProperty("rankType")
    private String rankType;

    /** 排序值（保留2位小数，涨停数为整数） */
    @JsonProperty("rankValue")
    private BigDecimal rankValue;

    /** 排名（从前1开始） */
    @JsonProperty("rank")
    private Integer rank;

    /** 排序方向: DESC/ASC */
    @JsonProperty("rankOrder")
    private String rankOrder;

    /** 领涨股票代码（成分股涨幅前9第一只） */
    @JsonProperty("topLeadStockCode")
    private String topLeadStockCode;

    /** 领涨股票名称 */
    @JsonProperty("topLeadStockName")
    private String topLeadStockName;

    /** 领涨股票涨幅（保留2位小数） */
    @JsonProperty("topLeadStockChangeRatio")
    private BigDecimal topLeadStockChangeRatio;

    /** 领涨股票持仓占比 */
    @JsonProperty("topLeadStockHoldRate")
    private BigDecimal topLeadStockHoldRate;

    /** 领跌股票代码（成分股涨幅后9第一只） */
    @JsonProperty("bottomLeadStockCode")
    private String bottomLeadStockCode;

    /** 领跌股票名称 */
    @JsonProperty("bottomLeadStockName")
    private String bottomLeadStockName;

    /** 领跌股票涨幅（保留2位小数） */
    @JsonProperty("bottomLeadStockChangeRatio")
    private BigDecimal bottomLeadStockChangeRatio;

    /** 领跌股票持仓占比 */
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
