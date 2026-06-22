package com.example.scheduledbach.listener;

import org.springframework.batch.core.BatchStatus;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.listener.JobExecutionListenerSupport;
import org.springframework.stereotype.Component;


/**
 * Listener para la finalización de trabajos por lotes.
 * Esta clase implementa el comportamiento a ejecutar después de que un trabajo por lotes termine,
 * mostrando en consola el estado del trabajo.
 */
@Component
public class JobCompletionListener extends JobExecutionListenerSupport {

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
