package com.example.BatchProcessor.config;

import com.zaxxer.hikari.HikariDataSource;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;


/**
 * Configuración de la base de datos utilizando HikariCP para la gestión de conexiones.
 * Esta clase lee los parámetros de conexión a la base de datos
 * y configura el DataSource para ser utilizado en la aplicación.
 */
@Configuration
public class DatabaseConfig {

    //Mediante esta implementacion estamos tomando los valores de la clase DataSourceConfigProperties que tenemos inyectada
    // Inyectar la clase DataSourceConfig que contiene las propiedades de la base de datos que comienzan por spring.datasource
    private final DataSourceConfigProperties dataSourceConfigProperties;

    public DatabaseConfig(DataSourceConfigProperties dataSourceConfigProperties) {
        this.dataSourceConfigProperties = dataSourceConfigProperties;
    }

    @Bean(name = "dataSource")
    public DataSource dataSource() {
        // Usar la configuración proporcionada por DataSourceConfig
        DataSourceConfigProperties.HikariConfig hikariConfig = dataSourceConfigProperties.getHikari();

        // Creamos un DataSource que servirá como gestor de conexiones a la base de datos, usamos hikari para reducir el costo de establecer nuevas conexiones constantemente
        // ya que nos permite: Reutilización de conexiones, Manejo automático de conexiones inactivas, Resiliencia y estabilidad, Configuración flexible y ademas Compatibilidad y estandarización
        HikariDataSource dataSource = new HikariDataSource();

        // Configuración del datasource
        dataSource.setJdbcUrl(dataSourceConfigProperties.getUrl());
        dataSource.setUsername(dataSourceConfigProperties.getUsername());
        dataSource.setPassword(dataSourceConfigProperties.getPassword());
        dataSource.setDriverClassName(dataSourceConfigProperties.getDriverClassName());
        dataSource.setMaximumPoolSize(hikariConfig.getMaximumPoolSize());
        dataSource.setMinimumIdle(hikariConfig.getMinimumIdle());
        dataSource.setIdleTimeout(hikariConfig.getIdleTimeout());
        dataSource.setConnectionTimeout(hikariConfig.getConnectionTimeout());
        dataSource.setMaxLifetime(hikariConfig.getMaxLifetime());

        return dataSource;
    }

    //Mediante esta implementacion estabamos leyendo desde el archivo de propiedades application.properties directamente

    /*@Value("${spring.datasource.url}")
    private String dbUrl;

    @Value("${spring.datasource.username}")
    private String dbUsername;

    @Value("${spring.datasource.password}")
    private String dbPassword;

    @Bean(name = "dataSource")
    public DataSource dataSource() {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(dbUrl);
        dataSource.setUsername(dbUsername);
        dataSource.setPassword(dbPassword);
        dataSource.setMaximumPoolSize(10); // Configuración opcional
        return dataSource;
    }*/


}