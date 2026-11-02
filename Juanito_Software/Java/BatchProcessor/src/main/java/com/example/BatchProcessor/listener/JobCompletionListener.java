package com.example.BatchProcessor.listener;

import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.listener.JobExecutionListenerSupport;
import org.springframework.stereotype.Component;


/**
 * Escucha de fin de job: escribe en la salida estándar si el job terminó bien
 * o falló.
 *
 * <p>{@code BatchController} lo engancha a cada job que compone. Como el
 * lanzador es síncrono y la respuesta HTTP no distingue éxito de fallo, este
 * mensaje (y las tablas {@code BATCH_*}) es la forma de saber cómo acabó una
 * ejecución.
 *
 * <p>{@code JobExecutionListenerSupport} está obsoleto desde Spring Batch 5:
 * lo moderno sería implementar {@code JobExecutionListener} directamente. Se
 * mantiene porque funciona igual.
 */
@Component
public class JobCompletionListener extends JobExecutionListenerSupport {

    /**
     * Se llama cuando el job termina, haya ido bien o no. Solo informa de
     * {@code COMPLETED} y {@code FAILED}; otros estados ({@code STOPPED},
     * {@code ABANDONED}...) no imprimen nada.
     *
     * @param jobExecution ejecución que acaba de terminar
     */
    @Override
    public void afterJob(JobExecution jobExecution) {

        if (jobExecution.getStatus() == BatchStatus.COMPLETED ) {
            System.out.println("Job finished with status: " + jobExecution.getStatus());

        }
        else if (jobExecution.getStatus() == BatchStatus.FAILED) {
            System.out.println("Job failure with status: " + jobExecution.getStatus());

        }

    }
}
