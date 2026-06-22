package com.example.scheduledbach.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

import javax.sql.DataSource;

@Configuration
public class DataSourceConfig {

    private final HikariConfigProperties hikariConfigProperties;
    private final PrimaryDataSourceProperties primaryProperties;
    private final SecondaryDataSourceProperties secondaryProperties;
    private final TertiaryDataSourceProperties tertiaryProperties;

    public DataSourceConfig(HikariConfigProperties hikariConfigProperties, PrimaryDataSourceProperties primaryProperties, SecondaryDataSourceProperties secondaryProperties, TertiaryDataSourceProperties tertiaryProperties) {
        this.hikariConfigProperties = hikariConfigProperties;
        this.primaryProperties = primaryProperties;
        this.secondaryProperties = secondaryProperties;
        this.tertiaryProperties = tertiaryProperties;

    }

    @Primary
    @Bean(name = "primaryDataSource")
    @Qualifier("primaryDataSource")
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
    @Qualifier("secondaryDataSource")
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

    @Bean(name = "tertiaryDataSource")
    @Qualifier("tertiaryDataSource")
    public DataSource tertiaryDataSource() {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(tertiaryProperties.getUrl());
        dataSource.setUsername(tertiaryProperties.getUsername());
        dataSource.setPassword(tertiaryProperties.getPassword());
        dataSource.setDriverClassName(tertiaryProperties.getDriverClassName());
        dataSource.setMaximumPoolSize(hikariConfigProperties.getMaximumPoolSize());
        dataSource.setMinimumIdle(hikariConfigProperties.getMinimumIdle());
        dataSource.setIdleTimeout(hikariConfigProperties.getIdleTimeout());
        dataSource.setConnectionTimeout(hikariConfigProperties.getConnectionTimeout());
        dataSource.setMaxLifetime(hikariConfigProperties.getMaxLifetime());
        return dataSource;
    }
}

