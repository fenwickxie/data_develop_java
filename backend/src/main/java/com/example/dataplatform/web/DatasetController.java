package com.example.dataplatform.web;

import com.example.dataplatform.raw.entity.Dataset;
import com.example.dataplatform.raw.service.DatasetService;
import com.example.dataplatform.web.dto.DatasetRequest;
import java.util.List;
import java.util.Optional;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.validation.annotation.Validated;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/datasets")
@Validated
@org.springframework.security.access.prepost.PreAuthorize("hasRole('USER')")
public class DatasetController {

    private final DatasetService datasetService;

    public DatasetController(DatasetService datasetService) {
        this.datasetService = datasetService;
    }

    @GetMapping
    public List<Dataset> listDatasets() {
        return datasetService.listDatasets();
    }

    @GetMapping("/{datasetId}")
    public ResponseEntity<Dataset> getDataset(@PathVariable String datasetId) {
        Optional<Dataset> dataset = datasetService.findDataset(datasetId);
        return dataset.map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Dataset> createOrUpdate(@Valid @RequestBody DatasetRequest request) {
        Dataset dataset = new Dataset();
        dataset.setDatasetId(request.getDatasetId());
        dataset.setName(request.getName());
        dataset.setDescription(request.getDescription());
        dataset.setStatus(request.getStatus());
        dataset.setCreatedBy(request.getCreatedBy());
        Dataset saved = datasetService.saveDataset(dataset);
        return ResponseEntity.ok(saved);
    }
}
