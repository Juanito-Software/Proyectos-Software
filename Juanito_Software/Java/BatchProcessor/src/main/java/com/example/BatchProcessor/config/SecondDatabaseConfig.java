package com.example.BatchProcessor.config;

import com.zaxxer.hikari.HikariDataSource;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateProperties;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateSettings;
import org.springframework.boot.autoconfigure.orm.jpa.JpaProperties;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;

import javax.sql.DataSource;
import java.util.Map;

/**
 * Segunda base de datos: la de destino de la ruta base de datos → base de datos.
 *
 * <p>Mover datos entre dos bases de datos no es solo tener dos
 * {@code DataSource}. Cada uno necesita su {@code EntityManagerFactory} y su
 * {@code TransactionManager}, y sobre todo: el paso de Spring Batch se ejecuta
 * dentro de **un** gestor de transacciones, y {@code JpaItemWriter} persiste con
 * el {@code EntityManager} asociado a ese gestor. Si el paso usa el gestor de la
 * primera base de datos y el escritor apunta a la segunda, la escritura falla
 * con «No EntityManager with actual transaction available».
 *
 * <p>Por eso el endpoint acepta un cuarto parámetro opcional con el nombre del
 * gestor de transacciones: quien lanza el job empareja escritor y gestor.
 *
 * <p>Ninguno de estos beans es primario. Todo lo que pida un
 * {@code DataSource}, una {@code EntityManagerFactory} o un
 * {@code TransactionManager} por tipo seguirá recibiendo los de la primera base
 * de datos, que es lo que usan las ocho rutas existentes.
 */
@Configuration
public class SecondDatabaseConfig {

    @Bean(name = "secondDataSource")
    public DataSource secondDataSource(
            @Value("${second.datasource.url}") String url,
            @Value("${second.datasource.username}") String usuario,
            @Value("${second.datasource.password}") String contrasena,
            @Value("${second.datasource.driver-class-name}") String driver) {

        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(url);
        dataSource.setUsername(usuario);
        dataSource.setPassword(contrasena);
        dataSource.setDriverClassName(driver);

        // Pool pequeño a propósito: esta base solo se usa como destino de una
        // ruta, no atiende peticiones.
        dataSource.setMaximumPoolSize(5);
        dataSource.setMinimumIdle(1);

        return dataSource;
    }

    @Bean(name = "secondEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean secondEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("secondDataSource") DataSource dataSource,
            JpaProperties jpaProperties,
            HibernateProperties hibernateProperties) {

        // Mismas propiedades de Hibernate que la principal, incluido ddl-auto.
        // Si no se pasan, el esquema de esta base no se crea y las escrituras
        // fallan con "tabla no encontrada".
        Map<String, Object> propiedades = hibernateProperties.determineHibernateProperties(
                jpaProperties.getProperties(), new HibernateSettings());

        return builder
                .dataSource(dataSource)
                .packages("com.example.BatchProcessor.model")
                .persistenceUnit("second")
                .properties(propiedades)
                .build();
    }

    @Bean(name = "secondTransactionManager")
    public JpaTransactionManager secondTransactionManager(
            @Qualifier("secondEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}
