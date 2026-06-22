package com.example.BatchProcessor.job;

import com.example.BatchProcessor.listener.JobCompletionListener;
import com.example.BatchProcessor.model.Persona;
import com.example.BatchProcessor.reader.CsvFileReader;
import com.example.BatchProcessor.service.RecordProcessor;
import com.example.BatchProcessor.writer.DatabaseWriter;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
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
public class FileProcessingJob {

    private final JobCompletionListener jobCompletionListener;  // Inyectamos el listener

    public FileProcessingJob(JobCompletionListener jobCompletionListener) {
        this.jobCompletionListener = jobCompletionListener;
    }

    @Bean(name = "job")
    public Job job(JobRepository jobRepository, Step step) {
        // Aquí pasamos el bean 'step' como parámetro
        return new JobBuilder("fileProcessingJob", jobRepository)
                .start(step)  // Referencia al metodo Step, que ya tiene los parámetros
                .listener(jobCompletionListener)  // Registramos el listener
                .build();
    }

    @Bean(name = "step") // procesamiento secuencial (en serie)
    public Step step(JobRepository jobRepository, JpaTransactionManager transactionManager,
                     CsvFileReader reader, RecordProcessor processor, DatabaseWriter writer) {
        // Aquí definimos el paso utilizando los beans y JobRepository
        return new StepBuilder("fileProcessingStep", jobRepository)
                .<Persona, Persona>chunk(10, transactionManager)  // Aquí defines el tamaño del chunk
                .reader(reader)
                .processor(processor)
                .writer(writer)
                //.taskExecutor(stepTaskExecutor)  // Usar TaskExecutor para paralelización en el procesamiento y escritura
                .build();
    }
}
