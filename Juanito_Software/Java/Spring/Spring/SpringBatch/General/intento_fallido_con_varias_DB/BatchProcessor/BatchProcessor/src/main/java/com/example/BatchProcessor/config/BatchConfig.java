package com.example.BatchProcessor.config;

import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.reader.CsvItemReader;
import com.example.BatchProcessor.reader.DatabaseReader;
import com.example.BatchProcessor.repository.GenericRepository;
import com.example.BatchProcessor.service.GenericProcessor;
import com.example.BatchProcessor.writer.CsvItemWriter;
import com.example.BatchProcessor.writer.DatabaseWriter;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.support.TaskExecutorJobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.support.JobRepositoryFactoryBean;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.ItemWriter;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.batch.item.database.JpaPagingItemReader;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.DataSourceBuilder;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.*;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.orm.jpa.vendor.HibernateJpaVendorAdapter;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import javax.sql.DataSource;
import java.sql.SQLException;
import java.util.Properties;


@EnableTransactionManagement
@EnableScheduling
@Configuration
//@PropertySource("classpath:application.properties")
public class BatchConfig {

    private final DataSource primaryDataSource;
    private final DataSource secondaryDataSource;

    public BatchConfig(
            @Qualifier("primaryDataSource") DataSource primaryDataSource,
            @Qualifier("secondaryDataSource") DataSource secondaryDataSource
    ) {
        this.primaryDataSource = primaryDataSource;
        this.secondaryDataSource = secondaryDataSource;
    }



    @Primary
    @Bean(name = "primaryJdbcTemplate")
    public JdbcTemplate primaryJdbcTemplate() {
        return new JdbcTemplate(primaryDataSource);
    }

    @Primary
    @Bean(name = "primaryEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean primaryEntityManagerFactory() {
        LocalContainerEntityManagerFactoryBean factory = new LocalContainerEntityManagerFactoryBean();
        factory.setDataSource(primaryDataSource);
        factory.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        factory.setPackagesToScan("com.example.BatchProcessor.model");
        Properties jpaProperties = new Properties();
        jpaProperties.put("hibernate.hbm2ddl.auto", "update"); // O "create", según lo necesites
        jpaProperties.put("hibernate.dialect", "org.hibernate.dialect.MySQLDialect"); // Asegúrate de usar el dialecto adecuado
        factory.setJpaProperties(jpaProperties);
        return factory;
    }

    @Primary
    @Bean(name = "primaryTransactionManager")
    public JpaTransactionManager primaryTransactionManager(@Qualifier("primaryEntityManagerFactory") EntityManagerFactory primaryEntityManagerFactory) {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(primaryEntityManagerFactory);
        return transactionManager;
    }

    @Bean(name = "jobRepository")
    public JobRepository jobRepository(@Qualifier("primaryTransactionManager") JpaTransactionManager primaryTransactionManager) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(primaryDataSource);
        factory.setTransactionManager(primaryTransactionManager);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet();
        return factory.getObject();
    }





    @Bean(name = "secondaryJdbcTemplate")
    public JdbcTemplate secondaryJdbcTemplate() {
        return new JdbcTemplate(secondaryDataSource);
    }

    @Bean(name = "secondEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean secondEntityManagerFactory() {
        LocalContainerEntityManagerFactoryBean factory = new LocalContainerEntityManagerFactoryBean();
        factory.setDataSource(secondaryDataSource);
        factory.setJpaVendorAdapter(new HibernateJpaVendorAdapter());
        factory.setPackagesToScan("com.example.BatchProcessor.model"); // Ajusta el paquete si es necesario

        Properties jpaProperties = new Properties();
        jpaProperties.put("hibernate.hbm2ddl.auto", "update");
        jpaProperties.put("hibernate.dialect", "org.hibernate.dialect.MySQLDialect");
        factory.setJpaProperties(jpaProperties);
        return factory;
    }

    @Bean(name = "secondTransactionManager")
    public JpaTransactionManager secondTransactionManager(
            @Qualifier("secondEntityManagerFactory") EntityManagerFactory secondEntityManagerFactory) {
        JpaTransactionManager transactionManager = new JpaTransactionManager();
        transactionManager.setEntityManagerFactory(secondEntityManagerFactory);
        return transactionManager;
    }

    @Bean(name = "jobRepository2")
    public JobRepository jobRepository2(@Qualifier("secondTransactionManager") JpaTransactionManager secondTransactionManager) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(secondaryDataSource);
        factory.setTransactionManager(secondTransactionManager);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet();
        return factory.getObject();
    }



    // Readers and Writers
    //csv
    @Bean(name = "csvItemReader")
    public CsvItemReader<GenericEntity> csvItemReader() {
        return new CsvItemReader<>(GenericEntity.class, new FlatFileItemReader<>());
    }

    @Bean(name = "csvItemWriter")
    public CsvItemWriter<GenericEntity> csvItemWriter() {
        return new CsvItemWriter<>();
    }
    //DB
    @StepScope
    @Bean(name = "databaseItemReader")
    public JpaPagingItemReader<?> databaseItemReader(
            @Qualifier("primaryEntityManagerFactory") EntityManagerFactory primaryEntityManagerFactory,
            @Value("#{jobParameters['entityClass']}") String entityClassName) throws ClassNotFoundException {
        return new DatabaseReader().databaseReader(primaryEntityManagerFactory, entityClassName);
    }

    @Bean(name = "databaseItemWriter")
    public <T> ItemWriter<T> databaseItemWriter(
            @Qualifier("primaryEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        JpaItemWriter<T> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }

    // leer de una base a otra, writer para escribir en la segunda
    @Bean(name = "databaseItemWriter2")
    @StepScope
    public <T> ItemWriter<T> databaseItemWriter2(
            @Qualifier("secondEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        JpaItemWriter<T> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }


    //processor
    @Bean
    public <T> GenericProcessor<T> genericProcessor() {
        return new GenericProcessor<>();
    }


    // Steps
    @Bean(name = "databaseToDatabaseStep")
    public Step databaseToDatabaseStep(
            @Qualifier("jobRepository2") JobRepository jobRepository,
            @Qualifier("secondTransactionManager") JpaTransactionManager transactionManager,
            @Qualifier("databaseItemReader") ItemReader<?> reader,
            @Qualifier("genericProcessor") ItemProcessor<?, ?> processor,
            @Qualifier("databaseItemWriter2") ItemWriter<?> writer) {
        return new StepBuilder("databaseToDatabaseStep", jobRepository)
                .<Object, Object>chunk(10, transactionManager)
                .reader(reader)
                .processor((ItemProcessor<? super Object, ?>) processor)
                .writer((ItemWriter<? super Object>) writer)
                .build();
    }
}
