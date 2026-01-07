package com.example.dataplatform.metrics.repository;

import com.example.dataplatform.metrics.entity.Report;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ReportRepository extends JpaRepository<Report, Long> {
    List<Report> findByDatasetId(String datasetId);

    List<Report> findByFileId(String fileId);
}
