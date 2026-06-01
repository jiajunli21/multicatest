package com.ifund.hq.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class EtfRankData {

    @JsonProperty("changeRatioTop9")
    private List<EtfRankItem> changeRatioTop9 = new ArrayList<>();

    @JsonProperty("changeRatioBottom9")
    private List<EtfRankItem> changeRatioBottom9 = new ArrayList<>();

    @JsonProperty("speedRatioTop9")
    private List<EtfRankItem> speedRatioTop9 = new ArrayList<>();

    @JsonProperty("speedRatioBottom9")
    private List<EtfRankItem> speedRatioBottom9 = new ArrayList<>();

    @JsonProperty("volumeRatioTop9")
    private List<EtfRankItem> volumeRatioTop9 = new ArrayList<>();

    @JsonProperty("volumeRatioBottom9")
    private List<EtfRankItem> volumeRatioBottom9 = new ArrayList<>();

    @JsonProperty("limitUpCountTop9")
    private List<EtfRankItem> limitUpCountTop9 = new ArrayList<>();

    @JsonProperty("limitUpCountBottom9")
    private List<EtfRankItem> limitUpCountBottom9 = new ArrayList<>();

    @JsonProperty("calcTimestamp")
    private Long calcTimestamp;

    @JsonProperty("calcDate")
    private String calcDate;

    public List<EtfRankItem> getChangeRatioTop9() {
        return changeRatioTop9;
    }

    public void setChangeRatioTop9(List<EtfRankItem> changeRatioTop9) {
        this.changeRatioTop9 = changeRatioTop9;
    }

    public List<EtfRankItem> getChangeRatioBottom9() {
        return changeRatioBottom9;
    }

    public void setChangeRatioBottom9(List<EtfRankItem> changeRatioBottom9) {
        this.changeRatioBottom9 = changeRatioBottom9;
    }

    public List<EtfRankItem> getSpeedRatioTop9() {
        return speedRatioTop9;
    }

    public void setSpeedRatioTop9(List<EtfRankItem> speedRatioTop9) {
        this.speedRatioTop9 = speedRatioTop9;
    }

    public List<EtfRankItem> getSpeedRatioBottom9() {
        return speedRatioBottom9;
    }

    public void setSpeedRatioBottom9(List<EtfRankItem> speedRatioBottom9) {
        this.speedRatioBottom9 = speedRatioBottom9;
    }

    public List<EtfRankItem> getVolumeRatioTop9() {
        return volumeRatioTop9;
    }

    public void setVolumeRatioTop9(List<EtfRankItem> volumeRatioTop9) {
        this.volumeRatioTop9 = volumeRatioTop9;
    }

    public List<EtfRankItem> getVolumeRatioBottom9() {
        return volumeRatioBottom9;
    }

    public void setVolumeRatioBottom9(List<EtfRankItem> volumeRatioBottom9) {
        this.volumeRatioBottom9 = volumeRatioBottom9;
    }

    public List<EtfRankItem> getLimitUpCountTop9() {
        return limitUpCountTop9;
    }

    public void setLimitUpCountTop9(List<EtfRankItem> limitUpCountTop9) {
        this.limitUpCountTop9 = limitUpCountTop9;
    }

    public List<EtfRankItem> getLimitUpCountBottom9() {
        return limitUpCountBottom9;
    }

    public void setLimitUpCountBottom9(List<EtfRankItem> limitUpCountBottom9) {
        this.limitUpCountBottom9 = limitUpCountBottom9;
    }

    public Long getCalcTimestamp() {
        return calcTimestamp;
    }

    public void setCalcTimestamp(Long calcTimestamp) {
        this.calcTimestamp = calcTimestamp;
    }

    public String getCalcDate() {
        return calcDate;
    }

    public void setCalcDate(String calcDate) {
        this.calcDate = calcDate;
    }
}
