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
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.jdbc.support.incrementer.AbstractDataFieldMaxValueIncrementer;
import org.springframework.jdbc.support.incrementer.DataFieldMaxValueIncrementer;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.transaction.PlatformTransactionManager;

import javax.sql.DataSource;
import java.util.Collection;


/**
 * Configuración de la ejecución de trabajos por lotes utilizando Spring Batch.
 * Esta clase configura los componentes principales para ejecutar un trabajo por lotes,
 * incluyendo el repositorio de trabajos, el lanzador de trabajos y la gestión de transacciones.
 */
@Configuration
@EnableBatchProcessing
public class BatchConfig {

    private DataSource dataSource;

    public BatchConfig(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @Bean(name = "jdbcTemplate")
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource);
    }

    // Configuración de PlatformTransactionManager
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

    // Configuración de JobLauncher
    @Bean(name = "jobLauncher")
    public JobLauncher jobLauncher(JobRepository jobRepository, @Qualifier("launcherTaskExecutor") TaskExecutor taskExecutor) throws Exception {
        TaskExecutorJobLauncher jobLauncher = new TaskExecutorJobLauncher();
        jobLauncher.setJobRepository(jobRepository);
        jobLauncher.setTaskExecutor(taskExecutor);  // Usamos el TaskExecutor ya configurado
        return jobLauncher;
    }

    // TaskExecutor dedicado a la ejecucion de trabajos(Jobs)
    @Bean(name = "launcherTaskExecutor")
    public TaskExecutor launcherTaskExecutor() {
        ThreadPoolTaskExecutor launcherExecutor = new ThreadPoolTaskExecutor();
        launcherExecutor.setCorePoolSize(5); // Número de hilos iniciales
        launcherExecutor.setMaxPoolSize(10); // Número máximo de hilos
        launcherExecutor.setQueueCapacity(5); // Tamaño de la cola de tareas
        launcherExecutor.setThreadNamePrefix("launcher-task-");
        launcherExecutor.initialize();
        // Añadir un Runnable para imprimir el nombre del hilo
        launcherExecutor.setTaskDecorator(task -> () -> {
            System.out.println("Thread name: " + Thread.currentThread().getName());  // Imprime el nombre del hilo
            task.run();  // Ejecuta la tarea
        });
        return launcherExecutor;
    }


    // TaskExecutor dedicado a la ejecucion de pasos(Steps)
    @Bean(name = "stepTaskExecutor")
    public TaskExecutor stepTaskExecutor() {
        ThreadPoolTaskExecutor stepExecutor = new ThreadPoolTaskExecutor();
        stepExecutor.setCorePoolSize(10); // Número de hilos iniciales
        stepExecutor.setMaxPoolSize(20); // Número máximo de hilos
        stepExecutor.setQueueCapacity(10); // Tamaño de la cola de tareas
        stepExecutor.setThreadNamePrefix("batch-task-");
        stepExecutor.initialize();
        // Añadir un Runnable para imprimir el nombre del hilo
        stepExecutor.setTaskDecorator(task -> () -> {
            System.out.println("Thread name: " + Thread.currentThread().getName());  // Imprime el nombre del hilo
            task.run();  // Ejecuta la tarea
        });
        return stepExecutor;
    }
}
