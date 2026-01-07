package com.example.dataplatform.web;

import com.example.dataplatform.raw.entity.FileRecord;
import com.example.dataplatform.raw.service.FileRecordService;
import com.example.dataplatform.service.SignedUrlService;
import com.example.dataplatform.web.dto.FileUploadRequest;
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
@RequestMapping("/api")
@Validated
@org.springframework.security.access.prepost.PreAuthorize("hasRole('USER')")
public class FileController {

    private final FileRecordService fileRecordService;
    private final SignedUrlService signedUrlService;

    public FileController(FileRecordService fileRecordService, SignedUrlService signedUrlService) {
        this.fileRecordService = fileRecordService;
        this.signedUrlService = signedUrlService;
    }

    @GetMapping("/datasets/{datasetId}/files")
    public List<FileRecord> listFiles(@PathVariable String datasetId) {
        return fileRecordService.listByDataset(datasetId);
    }

    @GetMapping("/files/{fileId}")
    public ResponseEntity<FileRecord> getFile(@PathVariable String fileId) {
        Optional<FileRecord> fileRecord = fileRecordService.findFile(fileId);
        return fileRecord.map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.notFound().build());
    }

    @GetMapping("/files/{fileId}/download-url")
    public ResponseEntity<SignedUrlResponse> getDownloadUrl(@PathVariable String fileId) {
        Optional<FileRecord> fileRecord = fileRecordService.findFile(fileId);
        return fileRecord
                .map(fr -> ResponseEntity.ok(new SignedUrlResponse(signedUrlService.generateDownloadUrl(fr))))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping("/datasets/{datasetId}/files")
    public ResponseEntity<FileRecord> createFile(
            @PathVariable String datasetId,
            @Valid @RequestBody FileUploadRequest request
    ) {
        FileRecord fr = new FileRecord();
        fr.setDatasetId(datasetId);
        fr.setFileId(request.getFileId());
        fr.setFilename(request.getFilename());
        fr.setBucket(request.getBucket());
        fr.setObjectKey(request.getObjectKey());
        fr.setStorageType(request.getStorageType());
        fr.setSize(request.getSize());
        fr.setChecksum(request.getChecksum());
        fr.setContentType(request.getContentType());
        fr.setVersion(request.getVersion());
        fr.setEncryptFlag(request.getEncryptFlag());
        fr.setStatus(request.getStatus());

        FileRecord saved = fileRecordService.saveFile(fr);
        return ResponseEntity.ok(saved);
    }

    @PostMapping("/files/upload-url")
    public ResponseEntity<SignedUrlResponse> createUploadUrl(
            @RequestParam String bucket,
            @RequestParam String objectKey
    ) {
        String url = signedUrlService.generateUploadUrl(bucket, objectKey);
        return ResponseEntity.ok(new SignedUrlResponse(url));
    }

    public record SignedUrlResponse(String url) {}
}
