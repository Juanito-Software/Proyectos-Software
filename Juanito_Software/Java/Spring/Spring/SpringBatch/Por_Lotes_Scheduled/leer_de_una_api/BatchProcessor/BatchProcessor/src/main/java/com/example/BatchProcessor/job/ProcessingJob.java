package com.example.BatchProcessor.job;

import com.example.BatchProcessor.listener.JobCompletionListener;
import com.example.BatchProcessor.model.Persona;
 // Importar correctamente el writer
import com.example.BatchProcessor.reader.ApiItemReader;
import com.example.BatchProcessor.service.PersonaItemProcessor;
import com.example.BatchProcessor.writer.PersonaItemWriter;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.orm.jpa.JpaTransactionManager;

/**
 * Configuración del trabajo por lotes que procesa un archivo CSV y escribe los resultados en la base de datos.
 * Esta clase define un trabajo por lotes que consiste en un solo paso, que incluye un lector de archivos CSV,
 * un procesador de registros y un escritor de base de datos.
 */
@Configuration
public class ProcessingJob {

    private final JobCompletionListener jobCompletionListener;

    public ProcessingJob(JobCompletionListener jobCompletionListener) {
        this.jobCompletionListener = jobCompletionListener;
    }

    @Bean(name = "httpJob")
    public Job job(JobRepository jobRepository, Step step) {
        return new JobBuilder("httpJob", jobRepository)
                .start(step)
                .listener(jobCompletionListener)
                .build();
    }

    @Bean(name = "httpStep")
    public Step step(JobRepository jobRepository, JpaTransactionManager transactionManager,
                     ApiItemReader reader, PersonaItemProcessor processor, PersonaItemWriter writer) {
        return new StepBuilder("httpStep", jobRepository)
                .<Persona, Persona>chunk(10, transactionManager)
                .reader(reader)
                .processor(processor)
                .writer(writer)
                .build();
    }
}
