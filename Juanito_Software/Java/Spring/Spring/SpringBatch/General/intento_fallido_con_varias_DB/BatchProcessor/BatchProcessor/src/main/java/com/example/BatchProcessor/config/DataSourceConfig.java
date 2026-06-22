package com.example.BatchProcessor.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {

    private final HikariConfigProperties hikariConfigProperties;
    private final PrimaryDataSourceProperties primaryProperties;
    private final SecondaryDataSourceProperties secondaryProperties;


    public DataSourceConfig(HikariConfigProperties hikariConfigProperties, PrimaryDataSourceProperties primaryProperties, SecondaryDataSourceProperties secondaryProperties) {
        this.hikariConfigProperties = hikariConfigProperties;
        this.primaryProperties = primaryProperties;
        this.secondaryProperties = secondaryProperties;
    }

    @Primary
    @Bean(name = "primaryDataSource")
    public DataSource primaryDataSource() {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(primaryProperties.getUrl());
        dataSource.setUsername(primaryProperties.getUsername());
        dataSource.setPassword(primaryProperties.getPassword());
        dataSource.setDriverClassName(primaryProperties.getDriverClassName());
        dataSource.setMaximumPoolSize(hikariConfigProperties.getMaximumPoolSize());
        dataSource.setMinimumIdle(hikariConfigProperties.getMinimumIdle());
        dataSource.setIdleTimeout(hikariConfigProperties.getIdleTimeout());
        dataSource.setConnectionTimeout(hikariConfigProperties.getConnectionTimeout());
        dataSource.setMaxLifetime(hikariConfigProperties.getMaxLifetime());
        return dataSource;
    }

    @Bean(name = "secondaryDataSource")
    public DataSource secondaryDataSource() {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(secondaryProperties.getUrl());
        dataSource.setUsername(secondaryProperties.getUsername());
        dataSource.setPassword(secondaryProperties.getPassword());
        dataSource.setDriverClassName(secondaryProperties.getDriverClassName());
        dataSource.setMaximumPoolSize(hikariConfigProperties.getMaximumPoolSize());
        dataSource.setMinimumIdle(hikariConfigProperties.getMinimumIdle());
        dataSource.setIdleTimeout(hikariConfigProperties.getIdleTimeout());
        dataSource.setConnectionTimeout(hikariConfigProperties.getConnectionTimeout());
        dataSource.setMaxLifetime(hikariConfigProperties.getMaxLifetime());
        return dataSource;
    }
}

