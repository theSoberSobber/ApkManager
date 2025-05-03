package com.orvio.apkmanager.service;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import lombok.extern.slf4j.Slf4j;

@Service
@Slf4j
public class ApkStorageService {

    private final Path storageLocation;

    @Autowired
    public ApkStorageService(String storageLocation) {
        this.storageLocation = Paths.get(storageLocation);
    }

    /**
     * Stores a new APK file, handling the versioning logic.
     * If latest.apk exists, stores as latest_newer.apk
     */
    public String storeApk(MultipartFile file, String projectName) {
        try {
            if (file.isEmpty()) {
                throw new RuntimeException("Failed to store empty file");
            }

            // Create directory for the project if it doesn't exist
            Path projectDir = this.storageLocation.resolve(projectName);
            Files.createDirectories(projectDir);

            // Check if latest.apk exists
            Path latestApkPath = projectDir.resolve("latest.apk");
            Path newerApkPath = projectDir.resolve("latest_newer.apk");
            String filename;

            if (Files.exists(latestApkPath)) {
                // Store as latest_newer.apk
                filename = "latest_newer.apk";
                try (InputStream inputStream = file.getInputStream()) {
                    Files.copy(inputStream, newerApkPath, StandardCopyOption.REPLACE_EXISTING);
                }
                log.info("Stored new APK as latest_newer.apk for project: {}", projectName);
            } else {
                // Store as latest.apk
                filename = "latest.apk";
                try (InputStream inputStream = file.getInputStream()) {
                    Files.copy(inputStream, latestApkPath, StandardCopyOption.REPLACE_EXISTING);
                }
                log.info("Stored new APK as latest.apk for project: {}", projectName);
            }

            return filename;
        } catch (IOException e) {
            throw new RuntimeException("Failed to store file", e);
        }
    }

    /**
     * After download, replaces latest.apk with latest_newer.apk if it exists
     */
    public void rotateApksAfterDownload(String projectName) {
        try {
            Path projectDir = this.storageLocation.resolve(projectName);
            Path latestApkPath = projectDir.resolve("latest.apk");
            Path newerApkPath = projectDir.resolve("latest_newer.apk");

            if (Files.exists(newerApkPath)) {
                Files.move(newerApkPath, latestApkPath, StandardCopyOption.REPLACE_EXISTING);
                log.info("Rotated: latest_newer.apk is now latest.apk for project: {}", projectName);
            }
        } catch (IOException e) {
            log.error("Failed to rotate APKs after download", e);
        }
    }

    /**
     * Loads APK file as a Resource
     */
    public Resource loadApkAsResource(String projectName, String filename) {
        try {
            Path projectDir = this.storageLocation.resolve(projectName);
            Path filePath = projectDir.resolve(filename);
            Resource resource = new UrlResource(filePath.toUri());

            if (resource.exists() && resource.isReadable()) {
                return resource;
            } else {
                throw new RuntimeException("Could not read file: " + filename);
            }
        } catch (IOException e) {
            throw new RuntimeException("Could not read file: " + filename, e);
        }
    }
} 