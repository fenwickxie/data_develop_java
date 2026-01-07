package com.example.dataplatform.raw.service;

import com.example.dataplatform.raw.entity.FileRecord;
import com.example.dataplatform.raw.repository.FileRecordRepository;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true, transactionManager = "rawTransactionManager")
public class FileRecordService {

    private final FileRecordRepository fileRecordRepository;

    public FileRecordService(FileRecordRepository fileRecordRepository) {
        this.fileRecordRepository = fileRecordRepository;
    }

    public List<FileRecord> listByDataset(String datasetId) {
        return fileRecordRepository.findByDatasetId(datasetId);
    }

    public Optional<FileRecord> findFile(String fileId) {
        return fileRecordRepository.findById(fileId);
    }

    @Transactional(transactionManager = "rawTransactionManager")
    public FileRecord saveFile(FileRecord fileRecord) {
        if (fileRecord.getCreatedAt() == null) {
            fileRecord.setCreatedAt(OffsetDateTime.now(ZoneOffset.UTC));
        }
        return fileRecordRepository.save(fileRecord);
    }
}
