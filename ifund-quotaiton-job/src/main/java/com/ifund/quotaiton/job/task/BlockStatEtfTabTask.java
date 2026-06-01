package com.ifund.quotaiton.job.task;

import com.ifund.quotaiton.job.dto.EtfConstituentStockResponse.ConstituentStockItem;
import com.ifund.quotaiton.job.dto.EtfFundPoolResponse.EtfFundPoolItem;
import com.ifund.quotaiton.job.dto.EtfRankData;
import com.ifund.quotaiton.job.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Scheduled task: BlockStatEtfTabTask.
 * Runs every minute to refresh ETF ranking data for the plate statistics ETF tab.
 *
 * Data flow:
 * 1. Fetch industry-themed ETFs from fund pool (~90 items)
 * 2. Query Fuyou for real-time changeRatio/speedRatio/volumeRatio
 * 3. Query all-market stock change ratios (markets 17/33/177)
 * 4. Query constituent stocks for all ETFs
 * 5. Calculate 8 ranking lists (4 criteria x top9/bottom9)
 * 6. Compute leading/lagging constituent stocks
 * 7. Write to Redis key plateStatEtf:rank:data
 *
 * Contract: AD-001~AD-009, DI-001~DI-011.
 * Delivery: 流程验证版 - scaffold code, mock-ready.
 *
 * Fallback strategies:
 * - Fund pool empty -> skip Redis write
 * - Fuyou failure -> skip Redis write
 * - Constituent stock failure -> write rankings but leave lead stocks null
 * - Division by zero -> return 0
 */
@Component
public class BlockStatEtfTabTask {

    private static final Logger log = LoggerFactory.getLogger(BlockStatEtfTabTask.class);

    private final EtfFundPoolService fundPoolService;
    private final EtfFuyaoService fuyaoService;
    private final EtfConstituentStockService constituentStockService;
    private final EtfRankCalculationService rankCalculationService;
    private final EtfRedisService redisService;

    public BlockStatEtfTabTask(EtfFundPoolService fundPoolService,
                                EtfFuyaoService fuyaoService,
                                EtfConstituentStockService constituentStockService,
                                EtfRankCalculationService rankCalculationService,
                                EtfRedisService redisService) {
        this.fundPoolService = fundPoolService;
        this.fuyaoService = fuyaoService;
        this.constituentStockService = constituentStockService;
        this.rankCalculationService = rankCalculationService;
        this.redisService = redisService;
    }

    /**
     * Main scheduled execution.
     * Cron: every 60 seconds (configured via block-stat-etf-tab.cron).
     * Contract: IA-002.
     */
    @Scheduled(cron = "${block-stat-etf-tab.cron}")
    public void execute() {
        log.info("BlockStatEtfTabTask started");

        // Acquire distributed lock (SBLK-003)
        if (!redisService.tryLock()) {
            log.info("BlockStatEtfTabTask skipped: lock held by another instance");
            return;
        }

        try {
            runTask();
        } catch (Exception e) {
            log.error("BlockStatEtfTabTask failed with exception: {}", e.getMessage(), e);
        } finally {
            redisService.unlock();
            log.info("BlockStatEtfTabTask finished");
        }
    }

    private void runTask() {
        // Step 1: Fetch ETF list from fund pool (DI-001, AD-001)
        List<EtfFundPoolItem> etfItems = fundPoolService.fetchIndustryThemeEtfs();
        if (etfItems.isEmpty()) {
            log.warn("Fund pool returned empty ETF list, skipping Redis write (fallback per contract)");
            return;
        }
        log.info("Fetched {} ETFs from fund pool", etfItems.size());

        List<String> etfStockCodes = etfItems.stream()
                .map(EtfFundPoolItem::getStockCode)
                .filter(Objects::nonNull)
                .collect(Collectors.toList());

        // Step 2: Query Fuyou for real-time data (DI-002, DI-003, DI-004)
        Map<String, BigDecimal> changeRatios = fuyaoService.queryEtfChangeRatio(etfStockCodes);
        Map<String, BigDecimal> speedRatios = fuyaoService.queryEtfSpeedRatio(etfStockCodes);
        Map<String, BigDecimal> volumeRatios = fuyaoService.queryEtfVolumeRatio(etfStockCodes);

        // Fuyou failure check: if all three queries return empty, skip Redis write
        if (changeRatios.isEmpty() && speedRatios.isEmpty() && volumeRatios.isEmpty()) {
            log.warn("All Fuyou queries returned empty, skipping Redis write (fallback per contract)");
            return;
        }

        // Step 3: Build limitUpCount map from fund pool items (DI-005, AD-005)
        Map<String, BigDecimal> limitUpCounts = new HashMap<>();
        for (EtfFundPoolItem item : etfItems) {
            if (item.getStockCode() != null && item.getEtfLimitUpStockCnt() != null) {
                limitUpCounts.put(item.getStockCode(), BigDecimal.valueOf(item.getEtfLimitUpStockCnt()));
            }
        }

        // Step 4: Query all-market stock change ratios for constituent intersection (DI-007)
        Map<String, BigDecimal> allMarketChanges = fuyaoService.queryAllMarketStockChangeRatio();

        // Step 5: Query constituent stocks (DI-006) — get all ETF constituent stocks first
        // for lead stock computation on the ranked ETFs only
        Map<String, List<ConstituentStockItem>> allConstituents =
                constituentStockService.fetchConstituentStocks(etfStockCodes);

        // Step 6: Calculate rankings (AD-002~AD-009)
        EtfRankData rankData = rankCalculationService.calculate(
                etfItems, changeRatios, speedRatios, volumeRatios,
                limitUpCounts, allConstituents, allMarketChanges);

        // Step 7: Write to Redis (DI-011, AD-009)
        redisService.writeRankData(rankData);

        log.info("BlockStatEtfTabTask: wrote rank data to Redis key={}, calcDate={}",
                redisService.getRankDataKey(), rankData.getCalcDate());
    }
}
