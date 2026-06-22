package com.example.BatchProcessor.controller;

import com.example.BatchProcessor.model.Persona;
import com.example.BatchProcessor.reader.CsvFileReader;
import com.example.BatchProcessor.repository.PersonaRepository;
import com.example.BatchProcessor.service.PersonaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.JobExecutionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.InputStreamResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.view.RedirectView;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;


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
    private final PersonaService personaService;
    private final PersonaRepository personaRepository;

    @Autowired
    public BatchController(JobLauncher jobLauncher, Job fileProcessingJob, CsvFileReader csvFileReader, PersonaService personaService, PersonaRepository personaRepository) {
        this.jobLauncher = jobLauncher;
        this.fileProcessingJob = fileProcessingJob;
        this.csvFileReader = csvFileReader;
        this.personaService = personaService;
        this.personaRepository = personaRepository;
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

    @Operation(
            summary = "Carga de archivo CSV usando la ruta",
            description = "Ruta archivo CSV a procesar"
    )
    @PostMapping("/upload_Path")
    public ResponseEntity<String> startBatchJob(@RequestParam("ruta") @Parameter(description = "Ruta archivo CSV a procesar") String ruta) {
        try {
            // Pasar la ruta directamente al lector antes de ejecutar el trabajo
            csvFileReader.setFilePath(ruta);

            // jobLauncher es un componente de Spring Batch que se encarga de iniciar y ejecutar un trabajo (job). El metodo run es responsable de ejecutar el trabajo especificado con un conjunto de parámetros.
            jobLauncher.run(fileProcessingJob, new JobParametersBuilder()//JobParametersBuilder es una clase que ayuda a construir los parámetros que se pasarán al trabajo. Estos son valores que pueden ser utilizados dentro del job y sus pasos.
                    .addString("ruta", ruta + " " + System.currentTimeMillis())// Aqui añadimos el parametro de la ruta que obtenemos como parámetro en la solicitud HTTP del RequestParam
                    .toJobParameters());// Este paso es opcional pero mejora la trazabilidad, la flexibilidad y el mantenimiento del código, ademas de reducir el acoplamiento.

            return ResponseEntity.ok("Job started successfully!");
        } catch (JobExecutionException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Failed to start job: " + e.getMessage());
        }
    }

    @Operation(
            summary = "Carga de archivo CSV usando el archivo (NO USAR)",
            description = "Para cargar y procesar un archivo CSV ejecuta: @GetMapping /upload_web_FileExplorer y despues copia el enlace en el navegador"
    )
    @PostMapping("/upload_file")
    public ResponseEntity<String> startBatchJob2(@RequestParam("file") MultipartFile file) {

        try {
            // Obtener el InputStream del archivo cargado
            InputStream fileInputStream = file.getInputStream();

            // Establecer el InputStreamResource en el CsvFileReader
            csvFileReader.setResource(new InputStreamResource(fileInputStream)); // Usamos InputStreamResource

            // jobLauncher es un componente de Spring Batch que se encarga de iniciar y ejecutar un trabajo (job)
            jobLauncher.run(fileProcessingJob, new JobParametersBuilder()  // JobParametersBuilder ayuda a construir los parámetros para el job
                    .addString("fileName", file.getOriginalFilename() + " " + System.currentTimeMillis())  // Añadimos el parámetro del archivo
                    .toJobParameters());  // Convertimos a parámetros para ejecutar el job

            return new ResponseEntity<>("Archivo procesado correctamente", HttpStatus.OK);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error al procesar el archivo: " + e.getMessage());
        }
    }

    @Operation(
            summary = "Obtiene todas las personas procesadas",
            description = "Devuelve una lista de todas las personas almacenadas en la base de datos"
    )
    @GetMapping("/personas")
    public ResponseEntity<List<Persona>> getAllPersonas() {
        try {
            List<Persona> personas = personaService.findAll();
            return ResponseEntity.ok(personas);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }

    @PostMapping("/SavePersonas")
    public ResponseEntity<Void> savePersonas(@RequestBody ArrayList<Persona> personas) {
        try {
            personaRepository.saveAll(personas);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
}