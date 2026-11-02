package com.example.BatchProcessor.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Propiedades {@code spring.datasource.*} de la base de datos <b>principal</b>.
 *
 * <p>Las consume {@code DatabaseConfig} para construir el {@code DataSource} a
 * mano (con HikariCP) en lugar de dejar que lo haga la autoconfiguración de
 * Spring Boot. Los nombres siguen el enlace relajado de Spring: la propiedad
 * {@code spring.datasource.driver-class-name} llega a {@link #driverClassName}.
 *
 * <p>Los valores del pool son primitivos sin valor por defecto: si falta el
 * {@code application.properties} principal llegan a cero y HikariCP no
 * arranca. Por eso los tests usan un <i>perfil</i> que se superpone a ese
 * fichero en vez de sustituirlo (ver {@code application-test.properties}).
 */
@Configuration
@ConfigurationProperties(prefix = "spring.datasource") // Este prefijo asegura que solo las propiedades bajo spring.datasource sean mapeadas
public class DataSourceConfigProperties {

    /** URL JDBC de la base principal. */
    private String url;
    /** Usuario de la base principal. */
    private String username;
    /** Contraseña de la base principal. */
    private String password;
    /** Clase del driver JDBC ({@code com.mysql.cj.jdbc.Driver}, o el de H2 en tests). */
    private String driverClassName;
    /** Plataforma de la base; se mapea por compatibilidad, no se usa al construir el pool. */
    private String platform;
    /** Ajustes del pool HikariCP ({@code spring.datasource.hikari.*}). */
    private HikariConfig hikari = new HikariConfig(); // Para mapear propiedades específicas de HikariCP

    // Getters y setters: los usa Spring para enlazar las propiedades y
    // DatabaseConfig para leerlas. No tienen lógica.

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getDriverClassName() {
        return driverClassName;
    }

    public void setDriverClassName(String driverClassName) {
        this.driverClassName = driverClassName;
    }

    public String getPlatform() {
        return platform;
    }

    public void setPlatform(String platform) {
        this.platform = platform;
    }

    public HikariConfig getHikari() {
        return hikari;
    }

    public void setHikari(HikariConfig hikari) {
        this.hikari = hikari;
    }

    /**
     * Ajustes del pool de conexiones HikariCP. Los tiempos van en
     * milisegundos. Mismo significado que las propiedades homónimas de
     * HikariCP; sus valores están comentados en {@code application.properties}.
     */
    public static class HikariConfig {
        /** Número máximo de conexiones abiertas a la vez. */
        private int maximumPoolSize;
        /** Conexiones ociosas que el pool intenta mantener. */
        private int minimumIdle;
        /** Tiempo que una conexión ociosa puede esperar antes de cerrarse (ms). */
        private long idleTimeout;
        /** Espera máxima para obtener una conexión del pool (ms). */
        private long connectionTimeout;
        /** Vida máxima de una conexión antes de reciclarla (ms). */
        private long maxLifetime;

        // Getters y setters sin lógica, para el enlace de propiedades.

        public int getMaximumPoolSize() {
            return maximumPoolSize;
        }

        public void setMaximumPoolSize(int maximumPoolSize) {
            this.maximumPoolSize = maximumPoolSize;
        }

        public int getMinimumIdle() {
            return minimumIdle;
        }

        public void setMinimumIdle(int minimumIdle) {
            this.minimumIdle = minimumIdle;
        }

        public long getIdleTimeout() {
            return idleTimeout;
        }

        public void setIdleTimeout(long idleTimeout) {
            this.idleTimeout = idleTimeout;
        }

        public long getConnectionTimeout() {
            return connectionTimeout;
        }

        public void setConnectionTimeout(long connectionTimeout) {
            this.connectionTimeout = connectionTimeout;
        }

        public long getMaxLifetime() {
            return maxLifetime;
        }

        public void setMaxLifetime(long maxLifetime) {
            this.maxLifetime = maxLifetime;
        }
    }
}
