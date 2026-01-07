package com.example.dataplatform.raw.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.time.OffsetDateTime;

@Entity
@Table(name = "file")
public class FileRecord {

    @Id
    @Column(name = "file_id", nullable = false, updatable = false)
    @NotBlank
    private String fileId;

    @Column(name = "dataset_id", nullable = false)
    @NotBlank
    private String datasetId;

    @Column(name = "filename")
    @NotBlank
    private String filename;

    @Column(name = "storage_type")
    private String storageType;

    @Column(name = "bucket")
    @NotBlank
    private String bucket;

    @Column(name = "object_key")
    @NotBlank
    private String objectKey;

    @Column(name = "size")
    @NotNull
    private Long size;

    @Column(name = "checksum")
    private String checksum;

    @Column(name = "content_type")
    private String contentType;

    @Column(name = "version")
    private Integer version;

    @Column(name = "encrypt_flag")
    private Boolean encryptFlag;

    @Column(name = "status")
    private String status;

    @Column(name = "created_at")
    private OffsetDateTime createdAt;

    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public String getDatasetId() {
        return datasetId;
    }

    public void setDatasetId(String datasetId) {
        this.datasetId = datasetId;
    }

    public String getFilename() {
        return filename;
    }

    public void setFilename(String filename) {
        this.filename = filename;
    }

    public String getStorageType() {
        return storageType;
    }

    public void setStorageType(String storageType) {
        this.storageType = storageType;
    }

    public String getBucket() {
        return bucket;
    }

    public void setBucket(String bucket) {
        this.bucket = bucket;
    }

    public String getObjectKey() {
        return objectKey;
    }

    public void setObjectKey(String objectKey) {
        this.objectKey = objectKey;
    }

    public Long getSize() {
        return size;
    }

    public void setSize(Long size) {
        this.size = size;
    }

    public String getChecksum() {
        return checksum;
    }

    public void setChecksum(String checksum) {
        this.checksum = checksum;
    }

    public String getContentType() {
        return contentType;
    }

    public void setContentType(String contentType) {
        this.contentType = contentType;
    }

    public Integer getVersion() {
        return version;
    }

    public void setVersion(Integer version) {
        this.version = version;
    }

    public Boolean getEncryptFlag() {
        return encryptFlag;
    }

    public void setEncryptFlag(Boolean encryptFlag) {
        this.encryptFlag = encryptFlag;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public OffsetDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(OffsetDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
