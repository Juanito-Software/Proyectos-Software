package com.example.BatchProcessor.config;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobExecution;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersInvalidException;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobExecutionAlreadyRunningException;
import org.springframework.batch.core.repository.JobInstanceAlreadyCompleteException;
import org.springframework.batch.core.repository.JobRestartException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
//NO SE USA
@Component
public class BatchJobLauncher implements JobLauncher {
    @Override
    public JobExecution run(Job job, JobParameters jobParameters) throws JobExecutionAlreadyRunningException, JobRestartException, JobInstanceAlreadyCompleteException, JobParametersInvalidException {
        return null;
    }

    // no necesitamos joblauncher debido a que ya tenemos configurado el JobLauncher dentro de tu configuración de Spring Batch
    // (a través de la anotación @EnableBatchProcessing y las beans definidas), Spring se encarga de la ejecución de los trabajos de forma automática.

    /*private final JobLauncher jobLauncher;
    private final Job job;

    public BatchJobLauncher(JobLauncher jobLauncher, Job job) {
        this.jobLauncher = jobLauncher;
        this.job = job;
    }

    public void runJob() {
        try {
            jobLauncher.run(job, new org.springframework.batch.core.JobParameters());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }*/
}