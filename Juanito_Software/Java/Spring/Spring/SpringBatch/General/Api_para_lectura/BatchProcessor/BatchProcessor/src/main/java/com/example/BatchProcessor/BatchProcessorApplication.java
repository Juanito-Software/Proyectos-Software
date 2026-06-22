package com.example.BatchProcessor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.PropertySource;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
/**
 * Esta aplicacion SpringBatch cumple las siguientes funciones:
 * 1. Tipos de aplicaciones por lotes 		   --> 	validación, Aplicaciones de procesamiento y actualización
 * 2. Pasos de utilidad estándar 			   --> 	División, Fusionar
 * 3. Clasificación según la fuente de entrada -->	Controladas por archivos
 * 4. Estrategias de procesamiento por lotes   -->	Procesamiento por lotes en línea(Secuencial, no paralelo), aunque podemos modificarlo para que sea en linea(simultáneo, paralelo) (solo en el contexto de los steps dado que no tenemos mas jobs) usando threadpooltaskexecuttor para ello porque AsyncTaskExecutor no reutiliza hilos
 * 5. Estrategias de confirmación y bloqueo	   -->	Confirmación única al final del procesamiento
 */
//@PropertySource("classpath:music.properties") // para inyectar propiedades de archivos distintos
@SpringBootApplication
@EnableJpaRepositories(basePackages = "com.example.BatchProcessor.repository")
public class BatchProcessorApplication {

	public static void main(String[] args) {
		SpringApplication.run(BatchProcessorApplication.class, args);
	}

}


