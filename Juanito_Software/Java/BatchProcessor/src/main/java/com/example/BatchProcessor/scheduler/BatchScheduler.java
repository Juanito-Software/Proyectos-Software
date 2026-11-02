package com.example.BatchProcessor.scheduler;

import com.example.BatchProcessor.config.BatchJobProperties;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/**
 * Ejecución programada de jobs por expresión cron. <b>Desactivada.</b>
 *
 * <p>La clase existe pero su cuerpo está comentado, por dos motivos:
 * <ul>
 *   <li>Dependía de un bean {@code Job genericJob} que ya no existe: los jobs se
 *       componen en caliente en {@code BatchController}, a partir de los
 *       nombres de lector, procesador y escritor que llegan en la petición.</li>
 *   <li>Ni {@code @EnableScheduling} está activo (comentado en
 *       {@code BatchConfig}) ni {@code application.properties} define
 *       {@code batch.job.cron}.</li>
 * </ul>
 *
 * <p>Para reactivarla habría que decidir qué combinación de beans lanza el
 * cron, construir el job igual que el controlador, definir
 * {@code batch.job.cron} (se mapea en {@link BatchJobProperties}) y activar
 * {@code @EnableScheduling}.
 */
@Component
public class BatchScheduler {

    /*private final JobLauncher jobLauncher;
    private final Job genericJob;

    // Inyectar la expresión cron desde application.properties
    @Value("${batch.job.cron}")
    private String cronExpression;

    public BatchScheduler(JobLauncher jobLauncher, Job genericJob) {
        this.jobLauncher = jobLauncher;
        this.genericJob = genericJob;
    }

    // Usar el cron dinámico inyectado desde application.properties
    @Scheduled(cron = "${batch.job.cron}")
    public void ejecutarProcesoDeLote() {
        System.out.println("Ejecutando tarea programada según cron: " + cronExpression);
        try {
            System.out.println("Iniciando procesamiento por lotes...");
            jobLauncher.run(genericJob, new JobParametersBuilder()
                    .addString("jobParam", "value")
                    .toJobParameters());
            System.out.println("Proceso por lotes completado.");
        } catch (Exception e) {
            System.err.println("Error en el procesamiento por lotes: " + e.getMessage());
            e.printStackTrace();
        }
    }*/
}

