package com.orvio.apkmanager.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class StorageConfig {

    @Value("${apk.storage.location}")
    private String storageLocation;

    @Bean
    public String storageLocation() {
        Path path = Paths.get(storageLocation);
        try {
            Files.createDirectories(path);
        } catch (IOException e) {
            throw new RuntimeException("Could not initialize storage", e);
        }
        return storageLocation;
    }
} 