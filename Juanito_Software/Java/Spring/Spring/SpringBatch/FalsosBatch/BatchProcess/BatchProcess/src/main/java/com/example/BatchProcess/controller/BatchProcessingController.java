package com.example.BatchProcess.controller;

import com.example.BatchProcess.service.BatchProcessingService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/batch")
public class BatchProcessingController {

    private final BatchProcessingService batchProcessingService;

    // Constructor para inyectar el servicio
    public BatchProcessingController(BatchProcessingService batchProcessingService) {
        this.batchProcessingService = batchProcessingService;
    }

    @PostMapping("/process")
    public ResponseEntity<String> processBatch(
            @RequestParam String inputFilePath,
            @RequestParam String outputFolder) {
        try {
            // Llamada al proceso de lote
            batchProcessingService.processBatch(inputFilePath, outputFolder);
            return ResponseEntity.ok("Batch processing completed successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error during batch processing: " + e.getMessage());
        }
    }
}