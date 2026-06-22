package com.example.BatchProcessor.controller;

import com.example.BatchProcessor.listener.JobCompletionListener;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/batch")
public class BatchController {

    private final JobLauncher jobLauncher;
    private final ApplicationContext context;
    private final JpaTransactionManager jpaTransactionManager;
    private final JobRepository jobRepository;
    private final JobCompletionListener jobCompletionListener;
    private String entityClass;

    public BatchController(JobLauncher jobLauncher, ApplicationContext context, JpaTransactionManager jpaTransactionManager, JobRepository jobRepository, JobCompletionListener jobCompletionListener, @Value("${entityClass}") String entityClass) {
        this.jobLauncher = jobLauncher;
        this.context = context;
        this.jpaTransactionManager = jpaTransactionManager;
        this.jobRepository = jobRepository;
        this.jobCompletionListener = jobCompletionListener;
        this.entityClass = entityClass;
    }

    @PostMapping("/run")
    public ResponseEntity<String> runBatchJob(@RequestParam Map<String, String> params) {
        try {
            // Obtener los nombres de los componentes desde los parámetros
            String readerBean = params.get("reader");
            String processorBean = params.get("processor");
            String writerBean = params.get("writer");


            // Verificar si los parámetros son válidos
            if (readerBean == null || processorBean == null || writerBean == null) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("Debe proporcionar los parámetros 'reader', 'processor' y 'writer'.");
            }

            // Obtener los componentes desde el contexto de Spring
            ItemReader<?> reader = (ItemReader<?>) context.getBean(readerBean);
            ItemProcessor<?, ?> processor = (ItemProcessor<?, ?>) context.getBean(processorBean);
            ItemWriter<?> writer = (ItemWriter<?>) context.getBean(writerBean);

            // Crear el Step dinámicamente
            Step dynamicStep = new StepBuilder("dynamicStep", jobRepository)
                    .<Object, Object>chunk(10, jpaTransactionManager)  // Tamaño del chunk, puedes ajustarlo
                    .reader(reader)
                    .processor((ItemProcessor<? super Object, ?>) processor)
                    .writer((ItemWriter<? super Object>) writer)
                    .build();

            // Crear el Job dinámicamente
            Job dynamicJob = new JobBuilder("dynamicJob", jobRepository)
                    .start(dynamicStep)
                    .listener(jobCompletionListener)
                    .build();

            // Ejecutar el Job con los parámetros opcionales
            JobParameters jobParameters = new JobParametersBuilder()        //IMPORTANTE
                    .addString("entityClass", entityClass)
                    .addString("Fecha",  " " + System.currentTimeMillis())  // Añadimos el parámetro del archivo
                    .toJobParameters();

            jobLauncher.run(dynamicJob, jobParameters);

            return ResponseEntity.ok("Job started successfully!");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error starting job: " + e.getMessage());
        }
    }
}