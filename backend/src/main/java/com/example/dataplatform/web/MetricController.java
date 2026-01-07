package com.example.dataplatform.web;

import com.example.dataplatform.metrics.entity.MetricResult;
import com.example.dataplatform.metrics.service.MetricResultService;
import com.example.dataplatform.web.dto.MetricRequest;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Optional;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.validation.annotation.Validated;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/metrics")
@Validated
@org.springframework.security.access.prepost.PreAuthorize("hasRole('USER')")
public class MetricController {

    private final MetricResultService metricResultService;
    private final ObjectMapper objectMapper;

    public MetricController(MetricResultService metricResultService, ObjectMapper objectMapper) {
        this.metricResultService = metricResultService;
        this.objectMapper = objectMapper;
    }

    @GetMapping
    public List<MetricResult> listMetrics(
            @RequestParam(value = "datasetId", required = false) String datasetId,
            @RequestParam(value = "fileId", required = false) String fileId
    ) {
        return metricResultService.listMetrics(datasetId, fileId);
    }

    @GetMapping("/{id}")
    public ResponseEntity<MetricResult> getMetric(@PathVariable Long id) {
        Optional<MetricResult> metric = metricResultService.findById(id);
        return metric.map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<MetricResult> createMetric(@Valid @RequestBody MetricRequest request) throws JsonProcessingException {
        MetricResult metricResult = new MetricResult();
        metricResult.setDatasetId(request.getDatasetId());
        metricResult.setFileId(request.getFileId());
        metricResult.setMetricName(request.getMetricName());
        metricResult.setMetricType(request.getMetricType());
        metricResult.setSourceToolVersion(request.getSourceToolVersion());
        metricResult.setMetricValue(objectMapper.writeValueAsString(request.getMetricValue()));

        MetricResult saved = metricResultService.saveMetric(metricResult);
        return ResponseEntity.ok(saved);
    }
}
