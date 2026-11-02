package com.example.BatchProcessor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Punto de entrada de BatchProcessor.
 *
 * <p>Arranca el contexto de Spring Boot con todo lo que necesita el motor de
 * lotes: la configuración de Spring Batch ({@code config.BatchConfig}), las dos
 * bases de datos ({@code config.DatabaseConfig} y
 * {@code config.SecondDatabaseConfig}), los lectores, procesadores y
 * escritores que el endpoint {@code /batch/run} pide por nombre, y Swagger.
 *
 * <p>Las dos anotaciones de JPA fijan dónde buscar repositorios y entidades de
 * la base de datos <b>principal</b>. La segunda base se configura aparte, en
 * {@code SecondDatabaseConfig}, con las mismas entidades y sin repositorios.
 *
 * <p>{@code EnableScheduling} está importado pero no se usa: la ejecución
 * programada de {@code scheduler.BatchScheduler} está desactivada a propósito.
 */
@SpringBootApplication
@EnableJpaRepositories(basePackages = "com.example.BatchProcessor.repository")
@EntityScan(basePackages = "com.example.BatchProcessor.model") // Escanear las entidades
public class BatchProcessorApplication {

	/**
	 * Arranca la aplicación.
	 *
	 * @param args argumentos de línea de comandos; Spring Boot los acepta como
	 *             propiedades ({@code --server.port=9090}, por ejemplo)
	 */
	public static void main(String[] args) {
		SpringApplication.run(BatchProcessorApplication.class, args);
	}
}