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

            // jobLauncher es un componente de Spring Batch que se encarga de iniciar y ejecutar un trabajo (job). El metodo run es responsable de ejecutar el trabajo especificado con un conjunto de parámetros.
            jobLauncher.run(fileProcessingJob, new JobParametersBuilder()//JobParametersBuilder es una clase que ayuda a construir los parámetros que se pasarán al trabajo. Estos son valores que pueden ser utilizados dentro del job y sus pasos.
                    .addString("ruta", ruta)// Aqui añadimos el parametro de la ruta que obtenemos como parámetro en la solicitud HTTP del RequestParam
                    .toJobParameters());// Este paso es opcional pero mejora la trazabilidad, la flexibilidad y el mantenimiento del código, ademas de reducir el acoplamiento.

            return ResponseEntity.ok("Job started successfully!");
        } catch (JobExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to start job: " + e.getMessage());
        }
    }
}