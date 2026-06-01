package com.ifund.quotaiton.job.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import java.util.Map;

/**
 * Fuyou (扶摇) generic query request.
 * Follows query code table sections 2/4/5/6/7 request body structure.
 */
public class EtfFuyaoRequest {

    @JsonProperty("code_selectors")
    private List<Map<String, Object>> codeSelectors;

    @JsonProperty("indexes")
    private List<String> indexes;

    @JsonProperty("page_info")
    private PageInfo pageInfo;

    @JsonProperty("sort")
    private SortInfo sort;

    public List<Map<String, Object>> getCodeSelectors() {
        return codeSelectors;
    }

    public void setCodeSelectors(List<Map<String, Object>> codeSelectors) {
        this.codeSelectors = codeSelectors;
    }

    public List<String> getIndexes() {
        return indexes;
    }

    public void setIndexes(List<String> indexes) {
        this.indexes = indexes;
    }

    public PageInfo getPageInfo() {
        return pageInfo;
    }

    public void setPageInfo(PageInfo pageInfo) {
        this.pageInfo = pageInfo;
    }

    public SortInfo getSort() {
        return sort;
    }

    public void setSort(SortInfo sort) {
        this.sort = sort;
    }

    public static class PageInfo {
        @JsonProperty("page_size")
        private Integer pageSize;

        @JsonProperty("page_num")
        private Integer pageNum;

        public Integer getPageSize() {
            return pageSize;
        }

        public void setPageSize(Integer pageSize) {
            this.pageSize = pageSize;
        }

        public Integer getPageNum() {
            return pageNum;
        }

        public void setPageNum(Integer pageNum) {
            this.pageNum = pageNum;
        }
    }

    public static class SortInfo {
        @JsonProperty("field")
        private String field;

        @JsonProperty("order")
        private String order;

        public String getField() {
            return field;
        }

        public void setField(String field) {
            this.field = field;
        }

        public String getOrder() {
            return order;
        }

        public void setOrder(String order) {
            this.order = order;
        }
    }
}
