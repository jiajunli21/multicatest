package com.ifund.hq.controller;

import com.ifund.hq.dto.ApiResponse;
import com.ifund.hq.dto.EtfRankData;
import com.ifund.hq.dto.EtfRankItem;
import com.ifund.hq.service.EtfTabService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.List;

import static org.mockito.Mockito.when;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.startsWith;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(EtfTabController.class)
class EtfTabControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private EtfTabService etfTabService;

    private EtfRankData mockData;

    @BeforeEach
    void setUp() {
        mockData = new EtfRankData();
        mockData.setCalcTimestamp(1717200000000L);
        mockData.setCalcDate("2026-06-01");

        EtfRankItem item = new EtfRankItem();
        item.setStockCode("510050");
        item.setMarketCode("17");
        item.setName("华夏上证50ETF");
        item.setTradeCode("510050");
        item.setRankType("changeRatio");
        item.setRankValue(new BigDecimal("2.35"));
        item.setRank(1);
        item.setRankOrder("DESC");
        item.setTopLeadStockCode("600519");
        item.setTopLeadStockName("贵州茅台");
        item.setTopLeadStockChangeRatio(new BigDecimal("5.20"));
        item.setTopLeadStockHoldRate(new BigDecimal("15.30"));

        List<EtfRankItem> list = List.of(item);
        mockData.setChangeRatioTop9(list);
    }

    @Test
    void shouldReturnAllRankingsWhenNoRankType() throws Exception {
        when(etfTabService.getRankData()).thenReturn(mockData);

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("success"))
                .andExpect(jsonPath("$.data.changeRatioTop9[0].stockCode").value("510050"))
                .andExpect(jsonPath("$.data.changeRatioTop9[0].name").value("华夏上证50ETF"))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    void shouldFilterByRankType() throws Exception {
        when(etfTabService.getRankData()).thenReturn(mockData);
        when(etfTabService.filterByRankType(mockData, "changeRatio")).thenReturn(mockData);

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank")
                        .param("rankType", "changeRatio"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.changeRatioTop9[0].stockCode").value("510050"));
    }

    @Test
    void shouldRejectInvalidRankType() throws Exception {
        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank")
                        .param("rankType", "invalidType"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(400))
                .andExpect(jsonPath("$.message", startsWith("Invalid rankType: invalidType.")))
                .andExpect(jsonPath("$.message", containsString("changeRatio")))
                .andExpect(jsonPath("$.message", containsString("speedRatio")))
                .andExpect(jsonPath("$.message", containsString("volumeRatio")))
                .andExpect(jsonPath("$.message", containsString("limitUpCount")));
    }

    @Test
    void shouldReturnEmptyStructureOnCacheMiss() throws Exception {
        EtfRankData empty = new EtfRankData();
        when(etfTabService.getRankData()).thenReturn(empty);

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
