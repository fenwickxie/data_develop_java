package com.example.dataplatform.service;

import com.example.dataplatform.raw.entity.FileRecord;
import com.oracle.bmc.ConfigFileReader;
import com.oracle.bmc.auth.AuthenticationDetailsProvider;
import com.oracle.bmc.auth.ConfigFileAuthenticationDetailsProvider;
import com.oracle.bmc.objectstorage.ObjectStorage;
import com.oracle.bmc.objectstorage.ObjectStorageClient;
import com.oracle.bmc.objectstorage.requests.CreatePreauthenticatedRequestRequest;
import com.oracle.bmc.objectstorage.responses.CreatePreauthenticatedRequestResponse;
import com.oracle.bmc.objectstorage.model.CreatePreauthenticatedRequestDetails;
import com.oracle.bmc.objectstorage.model.PreauthenticatedRequest;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;

@Service
public class SignedUrlService {

    private static final Logger log = LoggerFactory.getLogger(SignedUrlService.class);

    @Value("${storage.ocy.base-url:https://ocy.example.com}")
    private String baseUrl;

    @Value("${storage.ocy.expiration-seconds:900}")
    private long expirationSeconds;

    @Value("${storage.ocy.namespace}")
    private String namespace;

    @Value("${storage.ocy.region:us-ashburn-1}")
    private String region;

    @Value("${storage.ocy.config-file:~/.oci/config}")
    private String configFile;

    @Value("${storage.ocy.profile:DEFAULT}")
    private String profile;

    @Value("${storage.ocy.bucket-name}")
    private String defaultBucket;

    private ObjectStorage objectStorageClient;
    private boolean ociEnabled = false;

    @PostConstruct
    public void init() {
        try {
            ConfigFileReader.ConfigFile config = ConfigFileReader.parse(configFile, profile);
            AuthenticationDetailsProvider provider = new ConfigFileAuthenticationDetailsProvider(config);
            objectStorageClient = ObjectStorageClient.builder()
                    .region(region)
                    .build(provider);
            ociEnabled = true;
            log.info("OCI Object Storage client initialized for region: {} namespace: {}", region, namespace);
        } catch (Exception e) {
            log.warn("Could not initialize OCI client: {}. Falling back to placeholder URLs.", e.getMessage());
            ociEnabled = false;
        }
    }

    public String generateDownloadUrl(FileRecord fileRecord) {
        if (!ociEnabled) {
            return String.format("%s/%s/%s?token=demo&expires=%d", baseUrl, fileRecord.getBucket(), fileRecord.getObjectKey(), expirationSeconds);
        }

        try {
            String bucket = fileRecord.getBucket() != null ? fileRecord.getBucket() : defaultBucket;
            CreatePreauthenticatedRequestDetails details = CreatePreauthenticatedRequestDetails.builder()
                    .name("download-" + System.currentTimeMillis())
                    .accessType(CreatePreauthenticatedRequestDetails.AccessType.ObjectRead)
                    .objectName(fileRecord.getObjectKey())
                    .timeExpires(Date.from(Instant.now().plus(expirationSeconds, ChronoUnit.SECONDS)))
                    .build();

            CreatePreauthenticatedRequestRequest request = CreatePreauthenticatedRequestRequest.builder()
                    .namespaceName(namespace)
                    .bucketName(bucket)
                    .createPreauthenticatedRequestDetails(details)
                    .build();

            CreatePreauthenticatedRequestResponse response = objectStorageClient.createPreauthenticatedRequest(request);
            PreauthenticatedRequest par = response.getPreauthenticatedRequest();
            
            String fullUrl = String.format("https://objectstorage.%s.oraclecloud.com%s", region, par.getAccessUri());
            log.debug("Generated download URL for object: {} in bucket: {}", fileRecord.getObjectKey(), bucket);
            return fullUrl;
        } catch (Exception e) {
            log.error("Failed to generate OCI download URL: {}", e.getMessage(), e);
            return String.format("%s/%s/%s?error=generation-failed", baseUrl, fileRecord.getBucket(), fileRecord.getObjectKey());
        }
    }

    public String generateUploadUrl(String bucket, String objectKey) {
        if (!ociEnabled) {
            return String.format("%s/%s/%s?upload=1&token=demo&expires=%d", baseUrl, bucket, objectKey, expirationSeconds);
        }

        try {
            String targetBucket = bucket != null ? bucket : defaultBucket;
            CreatePreauthenticatedRequestDetails details = CreatePreauthenticatedRequestDetails.builder()
                    .name("upload-" + System.currentTimeMillis())
                    .accessType(CreatePreauthenticatedRequestDetails.AccessType.ObjectWrite)
                    .objectName(objectKey)
                    .timeExpires(Date.from(Instant.now().plus(expirationSeconds, ChronoUnit.SECONDS)))
                    .build();

            CreatePreauthenticatedRequestRequest request = CreatePreauthenticatedRequestRequest.builder()
                    .namespaceName(namespace)
                    .bucketName(targetBucket)
                    .createPreauthenticatedRequestDetails(details)
                    .build();

            CreatePreauthenticatedRequestResponse response = objectStorageClient.createPreauthenticatedRequest(request);
            PreauthenticatedRequest par = response.getPreauthenticatedRequest();
            
            String fullUrl = String.format("https://objectstorage.%s.oraclecloud.com%s", region, par.getAccessUri());
            log.debug("Generated upload URL for object: {} in bucket: {}", objectKey, targetBucket);
            return fullUrl;
        } catch (Exception e) {
            log.error("Failed to generate OCI upload URL: {}", e.getMessage(), e);
            return String.format("%s/%s/%s?upload=1&error=generation-failed", baseUrl, bucket, objectKey);
        }
    }
}
