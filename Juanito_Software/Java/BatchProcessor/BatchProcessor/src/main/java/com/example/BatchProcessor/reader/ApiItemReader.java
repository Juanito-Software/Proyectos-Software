package com.example.BatchProcessor.reader;

import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.annotation.BeforeStep;
import org.springframework.batch.item.ItemReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * Lector de datos desde una API que lee los registros de la API y los mapea a objetos de tipo genérico.
 * Esta clase es utilizada por Spring Batch para leer datos desde una API y procesarlos por lotes.
 */
@Component
public class ApiItemReader<T> implements ItemReader<T> {
    private final RestTemplate restTemplate;
    private List<T> items;
    private int nextIndex=0;
    private Class<T> entityType;
    // URL de la API donde se leeran los datos
    private String apiUrl;

    // Constructor donde el tipo de objeto es pasado como parámetro
    public ApiItemReader(RestTemplateBuilder restTemplateBuilder, List<T> items, @Value("${apiToReadUrl}") String apiUrl) {
        this.restTemplate = restTemplateBuilder.build();
        this.items = items;
        this.apiUrl = apiUrl;
    }

    @BeforeStep
    public void beforeStep(StepExecution stepExecution) throws ClassNotFoundException {
        // Obtener el parámetro 'entityClass' desde los JobParameters
        String entityClassName = stepExecution.getJobParameters().getString("entityClass");

        if (entityClassName != null) {
            // Cargar la clase usando Class.forName y asignarla al tipo generico
            this.entityType = (Class<T>) Class.forName(entityClassName);
        } else {
            // Si no se pasa, manejar el error
            throw new IllegalArgumentException("Se debe proporcionar el parámetro 'entityClass'");
        }
    }

    @Override
    public T read() {
        if (items.isEmpty()) {
            // Llamada a la API para obtener los datos
            ParameterizedTypeReference<List<T>> typeReference = new ParameterizedTypeReference<List<T>>() {};
            ResponseEntity<List<T>> response = restTemplate.exchange(apiUrl, HttpMethod.GET, null, typeReference);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                items = response.getBody();
            } else {
                throw new RuntimeException("Error al obtener datos de la API");
            }
        }

        if (nextIndex < items.size()) {
            return items.get(nextIndex++);
        } else {
            return null; // Fin de los datos
        }
    }
}
