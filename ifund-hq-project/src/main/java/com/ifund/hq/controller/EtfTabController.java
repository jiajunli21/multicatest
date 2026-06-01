package com.ifund.hq.controller;

import com.ifund.hq.dto.ApiResponse;
import com.ifund.hq.dto.EtfRankData;
import com.ifund.hq.service.EtfTabService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Set;

@RestController
@RequestMapping("/quotation/plate_stat/etf_tab/v1")
public class EtfTabController {

    private static final Set<String> VALID_RANK_TYPES = Set.of(
            "changeRatio", "speedRatio", "volumeRatio", "limitUpCount"
    );

    private final EtfTabService etfTabService;

    public EtfTabController(EtfTabService etfTabService) {
        this.etfTabService = etfTabService;
    }

    @GetMapping("/rank")
    public ApiResponse<EtfRankData> getRank(
            @RequestParam(value = "rankType", required = false) String rankType) {

        if (rankType != null && !VALID_RANK_TYPES.contains(rankType)) {
            return ApiResponse.error(400,
                    "Invalid rankType: " + rankType + ". Allowed: " + VALID_RANK_TYPES);
        }

        EtfRankData fullData = etfTabService.getRankData();

        if (rankType != null) {
            return ApiResponse.success(etfTabService.filterByRankType(fullData, rankType));
        }

        return ApiResponse.success(fullData);
    }
}
