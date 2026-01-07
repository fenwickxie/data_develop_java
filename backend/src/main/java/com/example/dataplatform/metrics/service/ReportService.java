package com.example.dataplatform.metrics.service;

import com.example.dataplatform.metrics.entity.Report;
import com.example.dataplatform.metrics.repository.ReportRepository;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true, transactionManager = "metricsTransactionManager")
public class ReportService {

    private final ReportRepository reportRepository;

    public ReportService(ReportRepository reportRepository) {
        this.reportRepository = reportRepository;
    }

    public List<Report> listReports(String datasetId, String fileId) {
        if (fileId != null) {
            return reportRepository.findByFileId(fileId);
        }
        if (datasetId != null) {
            return reportRepository.findByDatasetId(datasetId);
        }
        return reportRepository.findAll();
    }

    public Optional<Report> findById(Long id) {
        return reportRepository.findById(id);
    }

    @Transactional(transactionManager = "metricsTransactionManager")
    public Report saveReport(Report report) {
        if (report.getGeneratedAt() == null) {
            report.setGeneratedAt(OffsetDateTime.now(ZoneOffset.UTC));
        }
        return reportRepository.save(report);
    }
}
