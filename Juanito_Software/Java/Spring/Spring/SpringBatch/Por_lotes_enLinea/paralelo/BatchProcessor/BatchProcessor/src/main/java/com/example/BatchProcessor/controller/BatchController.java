package com.example.BatchProcessor.controller;

import com.example.BatchProcessor.reader.CsvFileReader;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.JobExecutionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


/**
 * Controlador REST para manejar las solicitudes de ejecución de trabajos por lotes.
 * Este controlador expone un endpoint que permite iniciar un trabajo por lotes mediante una solicitud POST.
 */
@RestController
@RequestMapping("/batch")
public class BatchController {

    private final JobLauncher jobLauncher;
    private final Job fileProcessingJob;
    private final CsvFileReader csvFileReader;

    @Autowired
    public BatchController(JobLauncher jobLauncher, Job fileProcessingJob, CsvFileReader csvFileReader) {
        this.jobLauncher = jobLauncher;
        this.fileProcessingJob = fileProcessingJob;
        this.csvFileReader = csvFileReader;
    }

    /*@PostMapping("/start")
    public ResponseEntity<String> startBatchJob() {
        try {
            jobLauncher.run(fileProcessingJob, new org.springframework.batch.core.JobParameters());
            return ResponseEntity.ok("Job started successfully!");
        } catch (JobExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to start job: " + e.getMessage());
        }
    }*/

    @PostMapping("/start")
    public ResponseEntity<String> startBatchJob(@RequestParam("ruta") String ruta) {
        try {
            // Pasar la ruta directamente al lector antes de ejecutar el trabajo
            csvFileReader.setFilePath(ruta);

            jobLauncher.run(fileProcessingJob, new JobParametersBuilder()
                    .addString("ruta", ruta) // Para usarlo en el trabajo
                    .toJobParameters());

            return ResponseEntity.ok("Job started successfully!");
        } catch (JobExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to start job: " + e.getMessage());
        }
    }
}