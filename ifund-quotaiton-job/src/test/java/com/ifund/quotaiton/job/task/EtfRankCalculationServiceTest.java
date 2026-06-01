package com.ifund.quotaiton.job.task;

import com.ifund.quotaiton.job.dto.EtfConstituentStockResponse.ConstituentStockItem;
import com.ifund.quotaiton.job.dto.EtfFundPoolResponse.EtfFundPoolItem;
import com.ifund.quotaiton.job.dto.EtfRankData;
import com.ifund.quotaiton.job.dto.EtfRankItem;
import com.ifund.quotaiton.job.service.EtfRankCalculationService;

import java.math.BigDecimal;
import java.util.*;

/**
 * Manual test scaffolding for EtfRankCalculationService.
 * Validates:
 * - 8 ranking lists produced correctly
 * - Top 9 / Bottom 9 ordering
 * - 2 decimal precision for non-integer fields
 * - Integer precision for limitUpCount
 * - Leading/lagging stock computation
 */
public class EtfRankCalculationServiceTest {

    public static void main(String[] args) {
        EtfRankCalculationService service = new EtfRankCalculationService();

        // Build test data: 20 mock ETFs
        List<EtfFundPoolItem> etfItems = new ArrayList<>();
        Map<String, BigDecimal> changeRatios = new HashMap<>();
        Map<String, BigDecimal> speedRatios = new HashMap<>();
        Map<String, BigDecimal> volumeRatios = new HashMap<>();
        Map<String, BigDecimal> limitUpCounts = new HashMap<>();

        for (int i = 0; i < 20; i++) {
            String stockCode = "51" + String.format("%04d", i);
            EtfFundPoolItem item = new EtfFundPoolItem();
            item.setStockCode(stockCode);
            item.setMarket(i < 10 ? "17" : "33");
            item.setName("TestETF_" + i);
            item.setTradeCode("15" + String.format("%04d", i));
            item.setEtfLimitUpStockCnt((i * 7) % 15); // 0-14
            etfItems.add(item);

            changeRatios.put(stockCode, BigDecimal.valueOf((i - 5) * 1.5));
            speedRatios.put(stockCode, BigDecimal.valueOf((i - 3) * 0.3));
            volumeRatios.put(stockCode, BigDecimal.valueOf(0.5 + i * 0.15));
            limitUpCounts.put(stockCode, BigDecimal.valueOf(item.getEtfLimitUpStockCnt()));
        }

        // Build mock constituent stocks and all-market changes
        Map<String, List<ConstituentStockItem>> constituentMap = new HashMap<>();
        Map<String, BigDecimal> allMarketChanges = new HashMap<>();

        for (int i = 0; i < 20; i++) {
            String etfCode = "51" + String.format("%04d", i);
            List<ConstituentStockItem> constituents = new ArrayList<>();
            for (int j = 0; j < 5; j++) {
                String stockCode = "60" + String.format("%04d", i * 5 + j);
                ConstituentStockItem cs = new ConstituentStockItem();
                cs.setStockCode(etfCode);
                cs.setCode(stockCode);
                cs.setName("Stock_" + stockCode);
                cs.setMarketCode("17");
                cs.setEtfSecurityHoldrate(BigDecimal.valueOf(0.02 + j * 0.005));
                constituents.add(cs);
                allMarketChanges.put(stockCode, BigDecimal.valueOf((j - 2) * 2.5));
            }
            constituentMap.put(etfCode, constituents);
        }

        // Execute calculation
        EtfRankData result = service.calculate(
                etfItems, changeRatios, speedRatios, volumeRatios,
                limitUpCounts, constituentMap, allMarketChanges);

        // Verify results
        boolean allPassed = true;

        allPassed &= assertNotNull("changeRatioTop9", result.getChangeRatioTop9());
        allPassed &= assertSize("changeRatioTop9", result.getChangeRatioTop9(), 9);
        allPassed &= assertDescending("changeRatioTop9", result.getChangeRatioTop9());
        allPassed &= assertEquals("calcDate should be today", result.getCalcDate() != null, true);
        allPassed &= assertEquals("calcTimestamp should be set", result.getCalcTimestamp() > 0, true);

        allPassed &= assertNotNull("changeRatioBottom9", result.getChangeRatioBottom9());
        allPassed &= assertSize("changeRatioBottom9", result.getChangeRatioBottom9(), 9);
        allPassed &= assertAscending("changeRatioBottom9", result.getChangeRatioBottom9());

        allPassed &= assertNotNull("speedRatioTop9", result.getSpeedRatioTop9());
        allPassed &= assertSize("speedRatioTop9", result.getSpeedRatioTop9(), 9);

        allPassed &= assertNotNull("speedRatioBottom9", result.getSpeedRatioBottom9());
        allPassed &= assertSize("speedRatioBottom9", result.getSpeedRatioBottom9(), 9);

        allPassed &= assertNotNull("volumeRatioTop9", result.getVolumeRatioTop9());
        allPassed &= assertSize("volumeRatioTop9", result.getVolumeRatioTop9(), 9);

        allPassed &= assertNotNull("volumeRatioBottom9", result.getVolumeRatioBottom9());
        allPassed &= assertSize("volumeRatioBottom9", result.getVolumeRatioBottom9(), 9);

        allPassed &= assertNotNull("limitUpCountTop9", result.getLimitUpCountTop9());
        allPassed &= assertSize("limitUpCountTop9", result.getLimitUpCountTop9(), 9);

        allPassed &= assertNotNull("limitUpCountBottom9", result.getLimitUpCountBottom9());
        allPassed &= assertSize("limitUpCountBottom9", result.getLimitUpCountBottom9(), 9);

        // Verify leading/lagging stocks on first rank item
        EtfRankItem firstItem = result.getChangeRatioTop9().get(0);
        allPassed &= assertNotNull("topLeadStockCode", firstItem.getTopLeadStockCode());
        allPassed &= assertNotNull("topLeadStockName", firstItem.getTopLeadStockName());
        allPassed &= assertNotNull("bottomLeadStockCode", firstItem.getBottomLeadStockCode());
        allPassed &= assertNotNull("bottomLeadStockName", firstItem.getBottomLeadStockName());

        // Verify precision: rank values should have 2 decimal places (or 0 for limitUpCount)
        for (EtfRankItem item : result.getChangeRatioTop9()) {
            allPassed &= assertEquals("rankValue scale for changeRatio",
                    item.getRankValue().scale() <= 2, true);
        }
        for (EtfRankItem item : result.getLimitUpCountTop9()) {
            allPassed &= assertEquals("rankValue scale for limitUpCount should be 0",
                    item.getRankValue().scale(), 0);
        }

        // Verify rankOrder fields
        for (EtfRankItem item : result.getChangeRatioTop9()) {
            allPassed &= assertEquals("rankOrder", "DESC", item.getRankOrder());
        }
        for (EtfRankItem item : result.getChangeRatioBottom9()) {
            allPassed &= assertEquals("rankOrder", "ASC", item.getRankOrder());
        }

        if (allPassed) {
            System.out.println("ALL TESTS PASSED");
        } else {
            System.out.println("SOME TESTS FAILED");
            System.exit(1);
        }
    }

    private static boolean assertNotNull(String label, Object value) {
        if (value == null) {
            System.out.println("FAIL: " + label + " is null");
            return false;
        }
        System.out.println("PASS: " + label + " is not null");
        return true;
    }

    private static boolean assertSize(String label, List<?> list, int expected) {
        if (list.size() != expected) {
            System.out.println("FAIL: " + label + " size=" + list.size() + ", expected=" + expected);
            return false;
        }
        System.out.println("PASS: " + label + " size=" + expected);
        return true;
    }

    private static boolean assertEquals(String label, Object actual, Object expected) {
        if (!Objects.equals(actual, expected)) {
            System.out.println("FAIL: " + label + " actual=" + actual + ", expected=" + expected);
            return false;
        }
        System.out.println("PASS: " + label + " = " + expected);
        return true;
    }

    private static boolean assertDescending(String label, List<EtfRankItem> list) {
        for (int i = 0; i < list.size() - 1; i++) {
            BigDecimal current = list.get(i).getRankValue();
            BigDecimal next = list.get(i + 1).getRankValue();
            if (current.compareTo(next) < 0) {
                System.out.println("FAIL: " + label + " not descending at index " + i
                        + ": " + current + " < " + next);
                return false;
            }
        }
        System.out.println("PASS: " + label + " is descending");
        return true;
    }

    private static boolean assertAscending(String label, List<EtfRankItem> list) {
        for (int i = 0; i < list.size() - 1; i++) {
            BigDecimal current = list.get(i).getRankValue();
            BigDecimal next = list.get(i + 1).getRankValue();
            if (current.compareTo(next) > 0) {
                System.out.println("FAIL: " + label + " not ascending at index " + i
                        + ": " + current + " > " + next);
                return false;
            }
        }
        System.out.println("PASS: " + label + " is ascending");
        return true;
    }
}
