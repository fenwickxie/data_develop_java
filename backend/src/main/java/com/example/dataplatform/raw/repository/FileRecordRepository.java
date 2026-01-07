package com.example.dataplatform.raw.repository;

import com.example.dataplatform.raw.entity.FileRecord;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FileRecordRepository extends JpaRepository<FileRecord, String> {
    List<FileRecord> findByDatasetId(String datasetId);
}
