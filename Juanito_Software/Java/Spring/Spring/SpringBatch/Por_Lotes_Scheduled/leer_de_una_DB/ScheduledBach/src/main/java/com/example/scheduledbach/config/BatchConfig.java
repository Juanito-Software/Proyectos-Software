package com.example.scheduledbach.config;

import com.example.scheduledbach.reader.JpaItemReader;
import com.example.scheduledbach.repository.VentaRepository;
import com.example.scheduledbach.repository.VentaRepositoryTertiary;
import com.example.scheduledbach.writer.VentaItemWriter;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.support.TaskExecutorJobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.support.JobRepositoryFactoryBean;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import javax.sql.DataSource;
import java.util.Properties;

/**
 * Configuración de la ejecución de trabajos por lotes utilizando Spring Batch.
 * Esta clase configura los componentes principales para ejecutar un trabajo por lotes,
 * incluyendo el repositorio de trabajos, el lanzador de trabajos y la gestión de transacciones.
 */
@EnableScheduling
@Configuration
@EnableTransactionManagement
public class BatchConfig {

    private final DataSource secondaryDataSource;
    private final DataSource tertiaryDataSource; // Tercera base de datos

    public BatchConfig(
            @Qualifier("secondaryDataSource") DataSource secondaryDataSource,
            @Qualifier("tertiaryDataSource") DataSource tertiaryDataSource) {
        this.secondaryDataSource = secondaryDataSource;
        this.tertiaryDataSource = tertiaryDataSource;
    }


    // Configuración de JdbcTemplate para la creación de tablas (usando el segundo DataSource)
    @Bean(name = "jdbcTemplateSecondary")
    public JdbcTemplate jdbcTemplateSecondary() {
        return new JdbcTemplate(secondaryDataSource);
    }

    // Configuración de EntityManagerFactory para la base de datos secundaria (cambiado a 'entityManagerFactory')
    @Bean(name = "entityManagerFactory")  // Cambié el nombre a 'entityManagerFactory'
    @Primary
    public LocalContainerEntityManagerFactoryBean entityManagerFactory() {  // Cambié el nombre del metodo también
        LocalContainerEntityManagerFactoryBean factory = new LocalContainerEntityManagerFactoryBean();
        factory.setDataSource(secondaryDataSource);
        factory.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        factory.setPackagesToScan("com/example/scheduledbach/models"); // Paquete donde están las entidades JPA

        Properties jpaProperties = new Properties();
        jpaProperties.put("hibernate.hbm2ddl.auto", "update"); // O "create", según lo necesites
        jpaProperties.put("hibernate.dialect", "org.hibernate.dialect.MySQLDialect"); // Asegúrate de usar el dialecto adecuado
        factory.setJpaProperties(jpaProperties);
        return factory;
    }

    // Configuración de JpaTransactionManager para la base de datos secundaria
    @Bean(name = "transactionManager")
    @Primary
    @Qualifier("transactionManager")
    public JpaTransactionManager transactionManager(
            @Qualifier("entityManagerFactory") EntityManagerFactory entityManagerFactory) {  // Cambié el nombre aquí también
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(entityManagerFactory);
        return transactionManager;
    }

    // Configuración de JobRepository utilizando la base de datos secundaria
    @Bean(name = "jobRepositorySecondary")
    public JobRepository jobRepositorySecondary(@Qualifier("transactionManager") JpaTransactionManager transactionManagerSecondary) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(secondaryDataSource); // Usa el segundo DataSource
        factory.setTransactionManager(transactionManagerSecondary);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet(); // Inicializa el factory
        return factory.getObject();
    }




    // Configuración de JdbcTemplate para la tercera base de datos
    @Bean(name = "jdbcTemplateTertiary")
    public JdbcTemplate jdbcTemplateTertiary() {
        return new JdbcTemplate(tertiaryDataSource);
    }

    // Configuración de JpaTransactionManager para la tercera base de datos
    @Bean(name = "transactionManagerTertiary")
    @Qualifier("transactionManagerTertiary")
    public JpaTransactionManager transactionManagerTertiary(
            @Qualifier("entityManagerFactoryTertiary") EntityManagerFactory entityManagerFactoryTertiary) {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(entityManagerFactoryTertiary);
        return transactionManager;
    }

    // Configuración de EntityManagerFactory para la tercera base de datos
    @Bean(name = "entityManagerFactoryTertiary")
    public LocalContainerEntityManagerFactoryBean entityManagerFactoryTertiary() {
        LocalContainerEntityManagerFactoryBean factory = new LocalContainerEntityManagerFactoryBean();
        factory.setDataSource(tertiaryDataSource);
        factory.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        factory.setPackagesToScan("com.example.scheduledbach.models"); // Ajusta el paquete si es necesario

        Properties jpaProperties = new Properties();
        jpaProperties.put("hibernate.hbm2ddl.auto", "update");
        jpaProperties.put("hibernate.dialect", "org.hibernate.dialect.MySQLDialect");
        factory.setJpaProperties(jpaProperties);
        return factory;
    }

    // Configuración de JobRepository para la tercera base de datos
    @Bean(name = "jobRepositoryTertiary")
    public JobRepository jobRepositoryTertiary(@Qualifier("transactionManagerTertiary") JpaTransactionManager transactionManagerTertiary) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(tertiaryDataSource);
        factory.setTransactionManager(transactionManagerTertiary);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet();
        return factory.getObject();
    }




    // Configuración de JobLauncher usando el JobRepository secundario
    @Bean(name = "jobLauncher")
    public JobLauncher jobLauncher(JobRepository jobRepositorySecondary) throws Exception {
        TaskExecutorJobLauncher jobLauncher = new TaskExecutorJobLauncher();
        jobLauncher.setJobRepository(jobRepositorySecondary);
        TaskExecutor taskExecutor = new SyncTaskExecutor();  // Ejecuta de manera sincrónica
        jobLauncher.setTaskExecutor(taskExecutor);  // Establecer el TaskExecutor
        return jobLauncher;
    }

    // Configuración de JpaItemReader para usar el repositorio JPA directamente
    @Bean
    public JpaItemReader jpaItemReader(VentaRepository ventaRepository) {
        return new JpaItemReader(ventaRepository);
    }


    // Configuración de JpaItemReader para usar el repositorio JPA directamente
    @Bean
    public VentaItemWriter ventaItemWriter(VentaRepositoryTertiary ventaRepository) {
        LocalContainerEntityManagerFactoryBean entityManagerFactoryTertiary = entityManagerFactoryTertiary();
        EntityManagerFactory entityManagerFactory = entityManagerFactoryTertiary.getObject(); // Obtén el EntityManagerFactory
        return new VentaItemWriter(entityManagerFactory);
    }


    // Esta configuracion debe ser descomentada si queremos usar una pool de hilos para el joblauncher (solo tenemos un job) y otra para los Steps (de esta manera tendremos varios hilos ejecutando la lectura procesamiento y escritura de los chunks de 10 de manera paralela)

    /*// Configuración de JobLauncher
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
        launcherExecutor.setThreadNamePrefix("Batch-Joblauncher-task-");
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
        stepExecutor.setThreadNamePrefix("Batch-Step-task-");
        stepExecutor.initialize();
        // Añadir un Runnable para imprimir el nombre del hilo
        stepExecutor.setTaskDecorator(task -> () -> {
            System.out.println("Thread name: " + Thread.currentThread().getName());  // Imprime el nombre del hilo
            task.run();  // Ejecuta la tarea
        });
        return stepExecutor;
    }*/
}

