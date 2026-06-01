package com.ifund.quotaiton.job.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * Fuyou (扶摇) query response.
 * Generic structure: code/message/data array of row objects.
 */
public class EtfFuyaoResponse {

    @JsonProperty("code")
    private Integer code;

    @JsonProperty("message")
    private String message;

    @JsonProperty("data")
    private List<Map<String, Object>> data;

    public Integer getCode() {
        return code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<Map<String, Object>> getData() {
        return data;
    }

    public void setData(List<Map<String, Object>> data) {
        this.data = data;
    }

    /**
     * Extract a BigDecimal field from a row, return null if missing.
     */
    public static BigDecimal getBigDecimal(Map<String, Object> row, String field) {
        Object val = row.get(field);
        if (val == null) {
            return null;
        }
        if (val instanceof BigDecimal) {
            return (BigDecimal) val;
        }
        return new BigDecimal(val.toString());
    }

    /**
     * Extract a String field from a row, return null if missing.
     */
    public static String getString(Map<String, Object> row, String field) {
        Object val = row.get(field);
        if (val == null) {
            return null;
        }
        return val.toString();
    }
}
