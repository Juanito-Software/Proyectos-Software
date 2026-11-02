package com.example.BatchProcessor.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Propiedades {@code batch.job.*} de {@code application.properties}.
 *
 * <p>Hoy solo mapea {@code batch.job.cron}, pensada para la ejecución
 * programada de {@code scheduler.BatchScheduler}. Ese planificador está
 * desactivado y la propiedad no se define, así que {@link #getCron()} devuelve
 * {@code null}; nada lo usa todavía.
 */
@Configuration
@ConfigurationProperties(prefix = "batch.job")
public class BatchJobProperties {

    /** Expresión cron de Spring (6 campos: segundo minuto hora día mes día-semana). */
    private String cron;

    /** @return la expresión cron configurada, o {@code null} si no se define */
    public String getCron() {
        return cron;
    }

    /** @param cron expresión cron; la rellena Spring al enlazar las propiedades */
    public void setCron(String cron) {
        this.cron = cron;
    }
}
