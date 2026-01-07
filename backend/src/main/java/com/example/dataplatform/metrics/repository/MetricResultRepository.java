package com.example.dataplatform.metrics.repository;

import com.example.dataplatform.metrics.entity.MetricResult;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MetricResultRepository extends JpaRepository<MetricResult, Long> {
    List<MetricResult> findByDatasetId(String datasetId);

    List<MetricResult> findByFileId(String fileId);
}
