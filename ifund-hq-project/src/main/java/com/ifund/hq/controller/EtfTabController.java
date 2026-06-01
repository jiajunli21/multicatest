package com.ifund.hq.controller;

import com.ifund.hq.dto.EtfRankData;
import com.ifund.hq.dto.EtfRankItem;
import com.ifund.hq.service.EtfTabService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/quotation/plate_stat/etf_tab/v1")
public class EtfTabController {

    private final EtfTabService etfTabService;

    public EtfTabController(EtfTabService etfTabService) {
        this.etfTabService = etfTabService;
    }

    @GetMapping(value = "/rank", produces = MediaType.APPLICATION_JSON_VALUE)
    public EtfRankData getRank(@RequestParam(required = false) String rankType) {
        EtfRankData data = etfTabService.getEtfRankData();
        if (data == null) {
            data = etfTabService.getEmptyRankData();
        }

        if (rankType == null || rankType.isEmpty()) {
            return data;
        }

        EtfRankData filtered = new EtfRankData();
        filtered.setCalcTimestamp(data.getCalcTimestamp());
        filtered.setCalcDate(data.getCalcDate());

        switch (rankType) {
            case "changeRatio":
                filtered.setChangeRatioTop9(data.getChangeRatioTop9());
                filtered.setChangeRatioBottom9(data.getChangeRatioBottom9());
                break;
            case "speedRatio":
                filtered.setSpeedRatioTop9(data.getSpeedRatioTop9());
                filtered.setSpeedRatioBottom9(data.getSpeedRatioBottom9());
                break;
            case "volumeRatio":
                filtered.setVolumeRatioTop9(data.getVolumeRatioTop9());
                filtered.setVolumeRatioBottom9(data.getVolumeRatioBottom9());
                break;
            case "limitUpCount":
                filtered.setLimitUpCountTop9(data.getLimitUpCountTop9());
                filtered.setLimitUpCountBottom9(data.getLimitUpCountBottom9());
                break;
            default:
                return data;
        }
        return filtered;
    }
}
