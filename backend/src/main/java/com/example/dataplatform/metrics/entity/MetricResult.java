package com.example.dataplatform.metrics.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import java.time.OffsetDateTime;

@Entity
@Table(name = "metric_result")
public class MetricResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "dataset_id", nullable = false)
    @NotBlank
    private String datasetId;

    @Column(name = "file_id", nullable = false)
    @NotBlank
    private String fileId;

    @Column(name = "metric_name")
    private String metricName;

    @Column(name = "metric_value", columnDefinition = "jsonb")
    private String metricValue;

    @Column(name = "metric_type")
    private String metricType;

    @Column(name = "calculated_at")
    private OffsetDateTime calculatedAt;

    @Column(name = "source_tool_version")
    private String sourceToolVersion;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

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

    public String getMetricValue() {
        return metricValue;
    }

    public void setMetricValue(String metricValue) {
        this.metricValue = metricValue;
    }

    public String getMetricType() {
        return metricType;
    }

    public void setMetricType(String metricType) {
        this.metricType = metricType;
    }

    public OffsetDateTime getCalculatedAt() {
        return calculatedAt;
    }

    public void setCalculatedAt(OffsetDateTime calculatedAt) {
        this.calculatedAt = calculatedAt;
    }

    public String getSourceToolVersion() {
        return sourceToolVersion;
    }

    public void setSourceToolVersion(String sourceToolVersion) {
        this.sourceToolVersion = sourceToolVersion;
    }
}
