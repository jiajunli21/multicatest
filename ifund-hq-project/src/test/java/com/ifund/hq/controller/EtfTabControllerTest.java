package com.ifund.hq.controller;

import com.ifund.hq.dto.EtfRankData;
import com.ifund.hq.dto.EtfRankItem;
import com.ifund.hq.service.EtfTabService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.util.Arrays;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(EtfTabController.class)
class EtfTabControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private EtfTabService etfTabService;

    @Test
    void shouldReturnEmptyRankDataWhenServiceReturnsNull() throws Exception {
        when(etfTabService.getEtfRankData()).thenReturn(null);
        when(etfTabService.getEmptyRankData()).thenReturn(new EtfRankData());

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.changeRatioTop9").isArray())
                .andExpect(jsonPath("$.changeRatioTop9").isEmpty())
                .andExpect(jsonPath("$.changeRatioBottom9").isArray())
                .andExpect(jsonPath("$.speedRatioTop9").isArray())
                .andExpect(jsonPath("$.speedRatioBottom9").isArray())
                .andExpect(jsonPath("$.volumeRatioTop9").isArray())
                .andExpect(jsonPath("$.volumeRatioBottom9").isArray())
                .andExpect(jsonPath("$.limitUpCountTop9").isArray())
                .andExpect(jsonPath("$.limitUpCountBottom9").isArray());
    }

    @Test
    void shouldReturnFullRankDataWhenServiceReturnsData() throws Exception {
        EtfRankData data = createSampleRankData();
        when(etfTabService.getEtfRankData()).thenReturn(data);

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.changeRatioTop9").isArray())
                .andExpect(jsonPath("$.changeRatioTop9.length()").value(1))
                .andExpect(jsonPath("$.changeRatioTop9[0].stockCode").value("510050"))
                .andExpect(jsonPath("$.changeRatioTop9[0].rankType").value("changeRatio"))
                .andExpect(jsonPath("$.calcTimestamp").value(1717200000000L))
                .andExpect(jsonPath("$.calcDate").value("2026-06-01"))
                .andExpect(jsonPath("$.speedRatioTop9").isArray())
                .andExpect(jsonPath("$.speedRatioTop9").isEmpty())
                .andExpect(jsonPath("$.volumeRatioTop9").isArray())
                .andExpect(jsonPath("$.volumeRatioTop9").isEmpty());
    }

    @Test
    void shouldFilterByRankTypeChangeRatio() throws Exception {
        EtfRankData data = createSampleRankData();
        when(etfTabService.getEtfRankData()).thenReturn(data);

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank")
                        .param("rankType", "changeRatio"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.changeRatioTop9").isArray())
                .andExpect(jsonPath("$.changeRatioTop9.length()").value(1))
                .andExpect(jsonPath("$.speedRatioTop9").isArray())
                .andExpect(jsonPath("$.speedRatioTop9").isEmpty());
    }

    @Test
    void shouldReturnAllWhenRankTypeIsUnknown() throws Exception {
        EtfRankData data = createSampleRankData();
        when(etfTabService.getEtfRankData()).thenReturn(data);

        mockMvc.perform(get("/quotation/plate_stat/etf_tab/v1/rank")
                        .param("rankType", "unknown"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.changeRatioTop9.length()").value(1));
    }

    private EtfRankData createSampleRankData() {
        EtfRankItem item = new EtfRankItem();
        item.setStockCode("510050");
        item.setMarketCode("17");
        item.setName("上证50ETF");
        item.setTradeCode("510050");
        item.setRankType("changeRatio");
        item.setRankValue(new BigDecimal("3.25"));
        item.setRank(1);
        item.setRankOrder("DESC");
        item.setTopLeadStockCode("600519");
        item.setTopLeadStockName("贵州茅台");
        item.setTopLeadStockChangeRatio(new BigDecimal("5.12"));
        item.setTopLeadStockHoldRate(new BigDecimal("15.30"));
        item.setBottomLeadStockCode("601318");
        item.setBottomLeadStockName("中国平安");
        item.setBottomLeadStockChangeRatio(new BigDecimal("-1.23"));
        item.setBottomLeadStockHoldRate(new BigDecimal("10.05"));

        EtfRankData data = new EtfRankData();
        data.setChangeRatioTop9(Arrays.asList(item));
        data.setCalcTimestamp(1717200000000L);
        data.setCalcDate("2026-06-01");
        return data;
    }
}
