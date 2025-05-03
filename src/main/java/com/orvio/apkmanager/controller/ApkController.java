package com.orvio.apkmanager.controller;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.orvio.apkmanager.service.ApkStorageService;

import lombok.extern.slf4j.Slf4j;

@RestController
@RequestMapping("/")
@Slf4j
public class ApkController {

    private final ApkStorageService storageService;
    
    @Value("${api.secret.key}")
    private String apiSecretKey;

    @Autowired
    public ApkController(ApkStorageService storageService) {
        this.storageService = storageService;
    }

    /**
     * Upload a new APK for a project
     */
    @PostMapping("/{projectName}/upload")
    public ResponseEntity<?> uploadApk(
            @PathVariable String projectName,
            @RequestParam("file") MultipartFile file,
            @RequestHeader("X-Secret-Key") String secretKey) {
        
        // Check secret key
        if (!apiSecretKey.equals(secretKey)) {
            log.warn("Unauthorized upload attempt for project: {}", projectName);
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid secret key");
        }
        
        try {
            String filename = storageService.storeApk(file, projectName);
            
            Map<String, String> response = new HashMap<>();
            response.put("status", "success");
            response.put("filename", filename);
            response.put("project", projectName);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("Failed to upload APK for project: " + projectName, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to upload APK: " + e.getMessage());
        }
    }

    /**
     * Download the latest APK for a project
     */
    @GetMapping("/{projectName}/latest.apk")
    public ResponseEntity<Resource> downloadLatestApk(@PathVariable String projectName) {
        try {
            Resource resource = storageService.loadApkAsResource(projectName, "latest.apk");
            
            // After successful download, rotate the APKs if needed
            storageService.rotateApksAfterDownload(projectName);
            
            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_OCTET_STREAM)
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + projectName + "-latest.apk\"")
                    .body(resource);
        } catch (Exception e) {
            log.error("Failed to download latest APK for project: " + projectName, e);
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * Get information about the available APKs for a project
     */
    @GetMapping("/{projectName}/info")
    public ResponseEntity<?> getApkInfo(@PathVariable String projectName) {
        try {
            Map<String, Object> info = new HashMap<>();
            info.put("project", projectName);
            
            // Check if latest.apk exists
            try {
                Resource latestResource = storageService.loadApkAsResource(projectName, "latest.apk");
                if (latestResource.exists()) {
                    info.put("hasLatest", true);
                    info.put("latestUrl", "/" + projectName + "/latest.apk");
                } else {
                    info.put("hasLatest", false);
                }
            } catch (Exception e) {
                info.put("hasLatest", false);
            }
            
            // Check if latest_newer.apk exists
            try {
                Resource newerResource = storageService.loadApkAsResource(projectName, "latest_newer.apk");
                if (newerResource.exists()) {
                    info.put("hasNewer", true);
                } else {
                    info.put("hasNewer", false);
                }
            } catch (Exception e) {
                info.put("hasNewer", false);
            }
            
            return ResponseEntity.ok(info);
        } catch (Exception e) {
            log.error("Failed to get APK info for project: " + projectName, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to get APK info: " + e.getMessage());
        }
    }
} 