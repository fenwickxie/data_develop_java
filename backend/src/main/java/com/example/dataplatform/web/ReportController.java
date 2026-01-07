package com.example.dataplatform.web;

import com.example.dataplatform.metrics.entity.Report;
import com.example.dataplatform.metrics.service.ReportService;
import com.example.dataplatform.web.dto.ReportRequest;
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
@RequestMapping("/api/reports")
@Validated
@org.springframework.security.access.prepost.PreAuthorize("hasRole('USER')")
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    @GetMapping
    public List<Report> listReports(
            @RequestParam(value = "datasetId", required = false) String datasetId,
            @RequestParam(value = "fileId", required = false) String fileId
    ) {
        return reportService.listReports(datasetId, fileId);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Report> getReport(@PathVariable Long id) {
        Optional<Report> report = reportService.findById(id);
        return report.map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Report> createReport(@Valid @RequestBody ReportRequest request) {
        Report report = new Report();
        report.setDatasetId(request.getDatasetId());
        report.setFileId(request.getFileId());
        report.setReportType(request.getReportType());
        report.setBucket(request.getBucket());
        report.setObjectKey(request.getObjectKey());
        report.setStorageType(request.getStorageType());
        Report saved = reportService.saveReport(report);
        return ResponseEntity.ok(saved);
    }
}
