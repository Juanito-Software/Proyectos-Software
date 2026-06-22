package com.example.BatchProcessor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableScheduling;


@SpringBootApplication
@EnableJpaRepositories(basePackages = "com.example.BatchProcessor.repository")
@EntityScan(basePackages = "com.example.BatchProcessor.model") // Escanear las entidades
public class BatchProcessorApplication {
	public static void main(String[] args) {
		SpringApplication.run(BatchProcessorApplication.class, args);
	}
}