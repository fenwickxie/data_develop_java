package com.example.dataplatform.raw.service;

import com.example.dataplatform.raw.entity.Dataset;
import com.example.dataplatform.raw.repository.DatasetRepository;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true, transactionManager = "rawTransactionManager")
public class DatasetService {

    private final DatasetRepository datasetRepository;

    public DatasetService(DatasetRepository datasetRepository) {
        this.datasetRepository = datasetRepository;
    }

    public List<Dataset> listDatasets() {
        return datasetRepository.findAll();
    }

    public Optional<Dataset> findDataset(String datasetId) {
        return datasetRepository.findById(datasetId);
    }

    @Transactional(transactionManager = "rawTransactionManager")
    public Dataset saveDataset(Dataset dataset) {
        if (dataset.getCreatedAt() == null) {
            dataset.setCreatedAt(OffsetDateTime.now(ZoneOffset.UTC));
        }
        return datasetRepository.save(dataset);
    }
}
