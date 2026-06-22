package com.example.BatchProcessor.job;

import com.example.BatchProcessor.listener.JobCompletionListener;
import com.example.BatchProcessor.model.Venta;
import com.example.BatchProcessor.reader.CsvItemReader;
import com.example.BatchProcessor.service.VentaItemProcessor;
import com.example.BatchProcessor.writer.VentaItemWriter; // Importar correctamente el writer
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

    private final JobCompletionListener jobCompletionListener;  // Inyectamos el listener

    // Constructor para inyectar el JobCompletionListener
    public ProcessingJob(JobCompletionListener jobCompletionListener) {
        this.jobCompletionListener = jobCompletionListener;
    }

    @Bean(name = "job")
    public Job job(JobRepository jobRepository, Step step) {
        // Aquí pasamos el bean 'step' como parámetro
        return new JobBuilder("ProcessingJob", jobRepository)
                .start(step)  // Referencia al metodo Step, que ya tiene los parámetros
                .listener(jobCompletionListener)  // Registramos el listener
                .build();
    }

    @Bean(name = "step")
    public Step step(JobRepository jobRepository, JpaTransactionManager transactionManager,
                     CsvItemReader reader, VentaItemProcessor processor, VentaItemWriter writer) {
        // Aquí definimos el paso utilizando los beans y JobRepository
        return new StepBuilder("ProcessingStep", jobRepository)
                .<Venta, Venta>chunk(10, transactionManager)  // Aquí defines el tamaño del chunk (10 elementos)
                .reader(reader)
                .processor(processor)
                .writer(writer)  // Usamos el VentaItemWriter correcto
                .build();
    }
}
