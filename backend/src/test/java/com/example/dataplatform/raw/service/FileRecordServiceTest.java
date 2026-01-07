package com.example.dataplatform.raw.service;

import com.example.dataplatform.raw.entity.FileRecord;
import com.example.dataplatform.raw.repository.FileRecordRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ActiveProfiles("test")
@Transactional
class FileRecordServiceTest {

    @Autowired
    private FileRecordService fileRecordService;

    @Autowired
    private FileRecordRepository fileRecordRepository;

    @Test
    void testSaveAndFindFile() {
        // Given
        FileRecord file = new FileRecord();
        file.setDatasetId("test-dataset");
        file.setFileId("test-file-001");
        file.setFilename("test.csv");
        file.setBucket("test-bucket");
        file.setObjectKey("test/path/test.csv");
        file.setStorageType("OCI");
        file.setSize(1024L);
        file.setStatus("UPLOADED");

        // When
        FileRecord saved = fileRecordService.saveFile(file);

        // Then
        assertThat(saved.getId()).isNotNull();
        assertThat(saved.getFileId()).isEqualTo("test-file-001");
        assertThat(saved.getCreatedAt()).isNotNull();

        // Verify retrieval
        Optional<FileRecord> found = fileRecordService.findFile("test-file-001");
        assertThat(found).isPresent();
        assertThat(found.get().getFilename()).isEqualTo("test.csv");
    }

    @Test
    void testListByDataset() {
        // Given
        FileRecord file1 = createTestFile("dataset-01", "file-01", "data1.csv");
        FileRecord file2 = createTestFile("dataset-01", "file-02", "data2.csv");
        FileRecord file3 = createTestFile("dataset-02", "file-03", "data3.csv");

        fileRecordService.saveFile(file1);
        fileRecordService.saveFile(file2);
        fileRecordService.saveFile(file3);

        // When
        List<FileRecord> dataset01Files = fileRecordService.listByDataset("dataset-01");
        List<FileRecord> dataset02Files = fileRecordService.listByDataset("dataset-02");

        // Then
        assertThat(dataset01Files).hasSize(2);
        assertThat(dataset02Files).hasSize(1);
        assertThat(dataset01Files).extracting("fileId").containsExactlyInAnyOrder("file-01", "file-02");
    }

    private FileRecord createTestFile(String datasetId, String fileId, String filename) {
        FileRecord file = new FileRecord();
        file.setDatasetId(datasetId);
        file.setFileId(fileId);
        file.setFilename(filename);
        file.setBucket("test-bucket");
        file.setObjectKey("path/" + filename);
        file.setStorageType("OCI");
        file.setSize(2048L);
        file.setStatus("UPLOADED");
        return file;
    }
}
