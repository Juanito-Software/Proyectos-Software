package com.example.BatchProcessor.scheduler;

import com.example.BatchProcessor.config.BatchJobProperties;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;



@Component
public class BatchScheduler {

    private final JobLauncher jobLauncher;
    private final Job job;

    // Inyectar la expresión cron desde application.properties
    @Value("${batch.job.cron}")
    private String cronExpression;

    public BatchScheduler(JobLauncher jobLauncher, Job job) {
        this.jobLauncher = jobLauncher;
        this.job = job;
    }

    // Usar el cron dinámico inyectado desde application.properties
    @Scheduled(cron = "${batch.job.cron}")
    public void ejecutarProcesoDeLote() {
        System.out.println("Ejecutando tarea programada según cron: " + cronExpression);
        try {
            System.out.println("Iniciando procesamiento por lotes...");
            jobLauncher.run(job, new JobParametersBuilder()
                    .addString("JobID", String.valueOf(System.currentTimeMillis()))
                    .toJobParameters());
            System.out.println("Proceso por lotes completado.");
        } catch (Exception e) {
            System.err.println("Error en el procesamiento por lotes: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

