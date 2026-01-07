package com.example.dataplatform.metrics.service;

import com.example.dataplatform.metrics.entity.MetricResult;
import com.example.dataplatform.metrics.repository.MetricResultRepository;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true, transactionManager = "metricsTransactionManager")
public class MetricResultService {

    private final MetricResultRepository metricResultRepository;

    public MetricResultService(MetricResultRepository metricResultRepository) {
        this.metricResultRepository = metricResultRepository;
    }

    public List<MetricResult> listMetrics(String datasetId, String fileId) {
        if (fileId != null) {
            return metricResultRepository.findByFileId(fileId);
        }
        if (datasetId != null) {
            return metricResultRepository.findByDatasetId(datasetId);
        }
        return metricResultRepository.findAll();
    }

    public Optional<MetricResult> findById(Long id) {
        return metricResultRepository.findById(id);
    }

    @Transactional(transactionManager = "metricsTransactionManager")
    public MetricResult saveMetric(MetricResult metricResult) {
        if (metricResult.getCalculatedAt() == null) {
            metricResult.setCalculatedAt(OffsetDateTime.now(ZoneOffset.UTC));
        }
        return metricResultRepository.save(metricResult);
    }
}
