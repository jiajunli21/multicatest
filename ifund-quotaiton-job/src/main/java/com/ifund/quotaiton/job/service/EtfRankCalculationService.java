package com.ifund.quotaiton.job.service;

import com.ifund.quotaiton.job.dto.EtfConstituentStockResponse.ConstituentStockItem;
import com.ifund.quotaiton.job.dto.EtfFundPoolResponse.EtfFundPoolItem;
import com.ifund.quotaiton.job.dto.EtfRankData;
import com.ifund.quotaiton.job.dto.EtfRankItem;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Core ranking calculation service.
 * Contract: AD-002~AD-009, DI-008~DI-010.
 *
 * Performs:
 * - Sorting by 4 criteria (changeRatio/speedRatio/volumeRatio/limitUpCount)
 * - Constituent stock intersection with all-market stocks for leading/lagging calculation
 * - 8 ranking lists assembly
 *
 * Rules:
 * - Top 9 DESC / Bottom 9 ASC
 * - stockCode dictionary order as tiebreaker
 * - 2 decimal precision (SBLK-005); limitUpCount is integer
 * - Division by zero -> default 0
 * - Missing sort field -> skip from that ranking
 */
@Service
public class EtfRankCalculationService {

    private static final Logger log = LoggerFactory.getLogger(EtfRankCalculationService.class);

    private static final int RANK_SIZE = 9;
    private static final int SCALE = 2;

    /**
     * Calculate all 8 ranking lists from raw data.
     */
    public EtfRankData calculate(List<EtfFundPoolItem> etfItems,
                                  Map<String, BigDecimal> changeRatios,
                                  Map<String, BigDecimal> speedRatios,
                                  Map<String, BigDecimal> volumeRatios,
                                  Map<String, BigDecimal> limitUpCounts,
                                  Map<String, List<ConstituentStockItem>> constituentMap,
                                  Map<String, BigDecimal> allMarketChanges) {

        EtfRankData rankData = new EtfRankData();
        rankData.setCalcTimestamp(System.currentTimeMillis());
        rankData.setCalcDate(LocalDate.now(ZoneId.of("Asia/Shanghai")).toString());

        // changeRatio ranking: AD-002, DI-002
        rankData.setChangeRatioTop9(buildRankList(etfItems, changeRatios,
                "changeRatio", "DESC", constituentMap, allMarketChanges));
        rankData.setChangeRatioBottom9(buildRankList(etfItems, changeRatios,
                "changeRatio", "ASC", constituentMap, allMarketChanges));

        // speedRatio ranking: AD-003, DI-003
        rankData.setSpeedRatioTop9(buildRankList(etfItems, speedRatios,
                "speedRatio", "DESC", constituentMap, allMarketChanges));
        rankData.setSpeedRatioBottom9(buildRankList(etfItems, speedRatios,
                "speedRatio", "ASC", constituentMap, allMarketChanges));

        // volumeRatio ranking: AD-004, DI-004
        rankData.setVolumeRatioTop9(buildRankList(etfItems, volumeRatios,
                "volumeRatio", "DESC", constituentMap, allMarketChanges));
        rankData.setVolumeRatioBottom9(buildRankList(etfItems, volumeRatios,
                "volumeRatio", "ASC", constituentMap, allMarketChanges));

        // limitUpCount ranking: AD-005, DI-005
        rankData.setLimitUpCountTop9(buildRankList(etfItems, limitUpCounts,
                "limitUpCount", "DESC", constituentMap, allMarketChanges));
        rankData.setLimitUpCountBottom9(buildRankList(etfItems, limitUpCounts,
                "limitUpCount", "ASC", constituentMap, allMarketChanges));

        log.info("Calculated 8 ranking lists: changeRatio(T9={}, B9={}), speedRatio(T9={}, B9={}), "
                        + "volumeRatio(T9={}, B9={}), limitUpCount(T9={}, B9={})",
                sizeOf(rankData.getChangeRatioTop9()), sizeOf(rankData.getChangeRatioBottom9()),
                sizeOf(rankData.getSpeedRatioTop9()), sizeOf(rankData.getSpeedRatioBottom9()),
                sizeOf(rankData.getVolumeRatioTop9()), sizeOf(rankData.getVolumeRatioBottom9()),
                sizeOf(rankData.getLimitUpCountTop9()), sizeOf(rankData.getLimitUpCountBottom9()));

        return rankData;
    }

    /**
     * Build a single ranking list (top 9 or bottom 9) for a given sort criterion.
     *
     * @param etfItems         All ETF items from fund pool
     * @param fieldValues      stockCode -> sort value for this criterion
     * @param rankType         changeRatio/speedRatio/volumeRatio/limitUpCount
     * @param rankOrder        DESC or ASC
     * @param constituentMap   ETF stockCode -> filtered constituent stocks
     * @param allMarketChanges All stock change ratios for constituent intersection
     */
    private List<EtfRankItem> buildRankList(List<EtfFundPoolItem> etfItems,
                                             Map<String, BigDecimal> fieldValues,
                                             String rankType,
                                             String rankOrder,
                                             Map<String, List<ConstituentStockItem>> constituentMap,
                                             Map<String, BigDecimal> allMarketChanges) {

        // Remove items missing the sort field
        List<EtfFundPoolItem> validItems = etfItems.stream()
                .filter(item -> item.getStockCode() != null && fieldValues.containsKey(item.getStockCode()))
                .collect(Collectors.toList());

        if (validItems.isEmpty()) {
            return Collections.emptyList();
        }

        // Sort by field value (DESC or ASC), tiebreaker: stockCode dictionary order
        Comparator<EtfFundPoolItem> comparator = (a, b) -> {
            BigDecimal va = fieldValues.get(a.getStockCode());
            BigDecimal vb = fieldValues.get(b.getStockCode());

            int cmp;
            if ("DESC".equals(rankOrder)) {
                cmp = vb.compareTo(va);
            } else {
                cmp = va.compareTo(vb);
            }
            if (cmp != 0) return cmp;

            // Tiebreaker: stockCode dictionary order (SBLK-004)
            String ca = a.getStockCode() != null ? a.getStockCode() : "";
            String cb = b.getStockCode() != null ? b.getStockCode() : "";
            return ca.compareTo(cb);
        };

        validItems.sort(comparator);

        // Take first RANK_SIZE (9)
        List<EtfFundPoolItem> topItems = validItems.subList(0, Math.min(RANK_SIZE, validItems.size()));

        // Build EtfRankItem list with leading/lagging stock calculation
        List<EtfRankItem> rankList = new ArrayList<>();
        for (int i = 0; i < topItems.size(); i++) {
            EtfFundPoolItem item = topItems.get(i);
            EtfRankItem rankItem = buildBaseRankItem(item, rankType,
                    fieldValues.get(item.getStockCode()), rankOrder, i + 1);

            // Compute leading/lagging stocks from constituent intersection (DI-008, DI-009, AD-008)
            computeLeadStocks(rankItem, item.getStockCode(), constituentMap, allMarketChanges);

            rankList.add(rankItem);
        }

        return rankList;
    }

    /**
     * Build a base EtfRankItem from fund pool data with rank value.
     */
    private EtfRankItem buildBaseRankItem(EtfFundPoolItem item,
                                           String rankType,
                                           BigDecimal rankValue,
                                           String rankOrder,
                                           int rank) {
        EtfRankItem rankItem = new EtfRankItem();
        rankItem.setStockCode(item.getStockCode());
        rankItem.setMarketCode(item.getMarket());
        rankItem.setName(item.getName());
        rankItem.setTradeCode(item.getTradeCode());
        rankItem.setRankType(rankType);
        rankItem.setRankOrder(rankOrder);
        rankItem.setRank(rank);

        // Precision: 2 decimals for most, integer for limitUpCount (SBLK-005)
        BigDecimal scaled;
        if (rankValue == null) {
            scaled = BigDecimal.ZERO;
        } else if ("limitUpCount".equals(rankType)) {
            scaled = rankValue.setScale(0, RoundingMode.HALF_UP);
        } else {
            scaled = rankValue.setScale(SCALE, RoundingMode.HALF_UP);
        }
        rankItem.setRankValue(scaled);

        return rankItem;
    }

    /**
     * Compute leading (topLead) and lagging (bottomLead) stocks for an ETF.
     * Contract: DI-008, DI-009, AD-008.
     *
     * Intersects ETF constituent stocks with all-market stock change ratios,
     * then takes the highest (topLead) and lowest (bottomLead) change ratio constituent.
     */
    private void computeLeadStocks(EtfRankItem rankItem,
                                    String etfStockCode,
                                    Map<String, List<ConstituentStockItem>> constituentMap,
                                    Map<String, BigDecimal> allMarketChanges) {

        List<ConstituentStockItem> constituents = constituentMap.get(etfStockCode);
        if (constituents == null || constituents.isEmpty() || allMarketChanges.isEmpty()) {
            // Constituent data missing -> leave lead fields null (fallback per contract)
            return;
        }

        // Build list of constituent stocks with their change ratios (交集计算 AD-008)
        List<StockChangeEntry> stockChanges = new ArrayList<>();
        for (ConstituentStockItem cs : constituents) {
            BigDecimal changeRatio = allMarketChanges.get(cs.getCode());
            if (changeRatio != null) {
                stockChanges.add(new StockChangeEntry(cs, changeRatio));
            }
        }

        if (stockChanges.isEmpty()) {
            return;
        }

        // Sort by changeRatio DESC
        stockChanges.sort((a, b) -> b.changeRatio.compareTo(a.changeRatio));

        // TopLead: first stock with highest changeRatio (前9第一只, DI-009)
        StockChangeEntry topLead = stockChanges.get(0);
        rankItem.setTopLeadStockCode(topLead.constituent.getCode());
        rankItem.setTopLeadStockName(topLead.constituent.getName());
        rankItem.setTopLeadStockChangeRatio(topLead.changeRatio.setScale(SCALE, RoundingMode.HALF_UP));
        rankItem.setTopLeadStockHoldRate(topLead.constituent.getEtfSecurityHoldrate() != null
                ? topLead.constituent.getEtfSecurityHoldrate().setScale(SCALE, RoundingMode.HALF_UP)
                : null);

        // BottomLead: last stock with lowest changeRatio (后9第一只, DI-009)
        StockChangeEntry bottomLead = stockChanges.get(stockChanges.size() - 1);
        rankItem.setBottomLeadStockCode(bottomLead.constituent.getCode());
        rankItem.setBottomLeadStockName(bottomLead.constituent.getName());
        rankItem.setBottomLeadStockChangeRatio(bottomLead.changeRatio.setScale(SCALE, RoundingMode.HALF_UP));
        rankItem.setBottomLeadStockHoldRate(bottomLead.constituent.getEtfSecurityHoldrate() != null
                ? bottomLead.constituent.getEtfSecurityHoldrate().setScale(SCALE, RoundingMode.HALF_UP)
                : null);
    }

    private static int sizeOf(List<?> list) {
        return list != null ? list.size() : 0;
    }

    private static class StockChangeEntry {
        final ConstituentStockItem constituent;
        final BigDecimal changeRatio;

        StockChangeEntry(ConstituentStockItem constituent, BigDecimal changeRatio) {
            this.constituent = constituent;
            this.changeRatio = changeRatio;
        }
    }
}
