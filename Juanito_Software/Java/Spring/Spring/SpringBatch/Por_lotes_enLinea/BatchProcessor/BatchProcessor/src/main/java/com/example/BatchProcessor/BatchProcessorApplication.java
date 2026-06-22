package com.example.BatchProcessor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
/**
 * Esta aplicacion SpringBatch cumple las siguientes funciones:
 * 1. Tipos de aplicaciones por lotes 		   --> 	validación, Aplicaciones de procesamiento y actualización
 * 2. Pasos de utilidad estándar 			   --> 	División, Fusionar
 * 3. Clasificación según la fuente de entrada -->	Controladas por archivos
 * 4. Estrategias de procesamiento por lotes   -->	Procesamiento normal durante una ventana de lote en modo fuera de línea
 * 5. Estrategias de confirmación y bloqueo	   -->	Confirmación única al final del procesamiento
 */
@SpringBootApplication
@EnableJpaRepositories(basePackages = "com.example.BatchProcessor.repository")
public class BatchProcessorApplication {

	public static void main(String[] args) {
		SpringApplication.run(BatchProcessorApplication.class, args);
	}

}


