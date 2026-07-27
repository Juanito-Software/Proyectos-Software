package com.example.BatchProcess.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

    private static final Logger log = LoggerFactory.getLogger(BatchProcessingController.class);

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
            log.error("Error al procesar el lote", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error during batch processing. Consulte los logs del servidor.");
        }
    }
}