package com.example.BatchProcessor;

import com.example.BatchProcessor.config.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Esta aplicacion SpringBatch cumple las siguientes funciones:
 * 1. Tipos de aplicaciones por lotes 		   --> 	validación, Aplicaciones de procesamiento y actualización
 * 2. Pasos de utilidad estándar 			   --> 	División, Fusionar
 * 3. Clasificación según la fuente de entrada -->	Controladas por archivos
 * 4. Estrategias de procesamiento por lotes   -->	Procesamiento normal durante una ventana de lote en modo fuera de línea
 * 5. Estrategias de confirmación y bloqueo	   -->	Confirmación única al final del procesamiento
 */

@SpringBootApplication(exclude={DataSourceAutoConfiguration.class})
@EnableJpaRepositories(basePackages = "com.example.BatchProcessor.repository")
@EntityScan(basePackages = "com.example.BatchProcessor.model") // Escanear las entidades
public class BatchProcessorApplication {

	public static void main(String[] args) {
		SpringApplication.run(BatchProcessorApplication.class, args);
	}
}