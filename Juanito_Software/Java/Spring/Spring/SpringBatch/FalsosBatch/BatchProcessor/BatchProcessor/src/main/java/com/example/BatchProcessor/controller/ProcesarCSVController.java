package com.example.BatchProcessor.controller;

import com.example.BatchProcessor.service.ProcesarCSVService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/Batch")
public class ProcesarCSVController {

    private final ProcesarCSVService procesarCSVService;

    // Constructor para inyectar el servicio
    public ProcesarCSVController(ProcesarCSVService procesarCSVService) {
        this.procesarCSVService = procesarCSVService;
    }

    @PostMapping("/process")
    public ResponseEntity<String> processBatch(@RequestParam String inputFilePath) {
        try {
            // Llamada al proceso de lote, pasando la ruta del archivo CSV
            procesarCSVService.procesarCsv(inputFilePath);
            return ResponseEntity.ok("Batch processing completed successfully.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error during batch processing: " + e.getMessage());
        }
    }
}

