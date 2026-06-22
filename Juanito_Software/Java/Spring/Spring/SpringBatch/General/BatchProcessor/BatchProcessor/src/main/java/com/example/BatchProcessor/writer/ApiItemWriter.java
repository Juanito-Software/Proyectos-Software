package com.example.BatchProcessor.writer;

import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.List;

/**
 * Escritor que envía datos procesados a una API mediante solicitudes POST.
 * Utilizado en el contexto de Spring Batch.
 */
@Component
public class ApiItemWriter<T> implements ItemWriter<T> {

    private final RestTemplate restTemplate;

    // URL de la API donde se enviarán los datos
    private String apiUrl;


    public ApiItemWriter(RestTemplateBuilder restTemplateBuilder, @Value("${apiToWriteUrl}") String apiUrl) {
        this.restTemplate = restTemplateBuilder.build();
        this.apiUrl = apiUrl;
    }

    @Override
    public void write(Chunk<? extends T> chunk) throws Exception {
        for (T item : chunk) {
            try {

                // Convertir el Chunk a una lista de objetos Persona
                List<T> items = (List<T>) chunk.getItems();

                // Realiza una solicitud POST a la API para cada elemento
                ResponseEntity<Void> response = restTemplate.postForEntity(apiUrl, items, Void.class);

                // Manejo de errores o validación de respuesta
                if (!response.getStatusCode().is2xxSuccessful()) {
                    throw new RuntimeException("Error al enviar datos a la API: " + response.getStatusCode());
                }
            } catch (Exception e) {
                // Manejo de excepciones
                throw new RuntimeException("Error al enviar el item a la API: " + item, e);
            }
        }
    }
}

