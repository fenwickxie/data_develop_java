package com.example.dataplatform.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public class MetricRequest {

    @NotBlank
    private String datasetId;

    @NotBlank
    private String fileId;

    @NotBlank
    private String metricName;

    @NotNull
    private Object metricValue;

    private String metricType;

    private String sourceToolVersion;

    public String getDatasetId() {
        return datasetId;
    }

    public void setDatasetId(String datasetId) {
        this.datasetId = datasetId;
    }

    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public String getMetricName() {
        return metricName;
    }

    public void setMetricName(String metricName) {
        this.metricName = metricName;
    }

    public Object getMetricValue() {
        return metricValue;
    }

    public void setMetricValue(Object metricValue) {
        this.metricValue = metricValue;
    }

    public String getMetricType() {
        return metricType;
    }

    public void setMetricType(String metricType) {
        this.metricType = metricType;
    }

    public String getSourceToolVersion() {
        return sourceToolVersion;
    }

    public void setSourceToolVersion(String sourceToolVersion) {
        this.sourceToolVersion = sourceToolVersion;
    }
}
