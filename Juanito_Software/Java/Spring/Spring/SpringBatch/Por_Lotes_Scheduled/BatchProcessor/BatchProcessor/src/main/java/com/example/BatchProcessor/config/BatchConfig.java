package com.example.BatchProcessor.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.batch.core.*;
import org.springframework.batch.core.configuration.annotation.EnableBatchProcessing;
import org.springframework.batch.core.explore.JobExplorer;
import org.springframework.batch.core.explore.support.JobExplorerFactoryBean;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.support.TaskExecutorJobLauncher;
import org.springframework.batch.core.repository.JobExecutionAlreadyRunningException;
import org.springframework.batch.core.repository.JobInstanceAlreadyCompleteException;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.JobRestartException;
import org.springframework.batch.core.repository.support.JobRepositoryFactoryBean;
import org.springframework.batch.item.database.support.DataFieldMaxValueIncrementerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.jdbc.support.incrementer.AbstractDataFieldMaxValueIncrementer;
import org.springframework.jdbc.support.incrementer.DataFieldMaxValueIncrementer;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.transaction.PlatformTransactionManager;

import javax.sql.DataSource;
import java.util.Collection;


/**
 * Configuración de la ejecución de trabajos por lotes utilizando Spring Batch.
 * Esta clase configura los componentes principales para ejecutar un trabajo por lotes,
 * incluyendo el repositorio de trabajos, el lanzador de trabajos y la gestión de transacciones.
 */
@EnableScheduling
@Configuration
public class BatchConfig {

    private DataSource dataSource;

    public BatchConfig(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    // Configuracion de JdbcTemplate
    @Bean(name = "jdbcTemplate")
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource);
    }

    // Configuración de JpaTransactionManager si no estuvieramos usando JPA usariamos PlatformTransactionManager
    @Bean(name = "transactionManager")
    public JpaTransactionManager transactionManager() {
        return new JpaTransactionManager();
    }


    // Configuración del JobRepository
    @Bean(name = "jobRepository")
    public JobRepository jobRepository(JpaTransactionManager transactionManager) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(dataSource);
        factory.setTransactionManager(transactionManager);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet(); // Inicializa el factory
        return factory.getObject();
    }

    // Configuración de JobLauncher usando TaskExecutorJobLauncher
    @Bean(name = "jobLauncher")
    public JobLauncher jobLauncher(JobRepository jobRepository) throws Exception {
        TaskExecutorJobLauncher jobLauncher = new TaskExecutorJobLauncher();
        jobLauncher.setJobRepository(jobRepository);

        // Configura un TaskExecutor (sincrónico o asincrónico)
        TaskExecutor taskExecutor = new SyncTaskExecutor();  // O usa SimpleAsyncTaskExecutor para asincrónico
        jobLauncher.setTaskExecutor(taskExecutor);  // Establecer el TaskExecutor
        return jobLauncher;
    }
}
