package com.orvio.apkmanager;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties
public class ApkManagerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApkManagerApplication.class, args);
    }
} 