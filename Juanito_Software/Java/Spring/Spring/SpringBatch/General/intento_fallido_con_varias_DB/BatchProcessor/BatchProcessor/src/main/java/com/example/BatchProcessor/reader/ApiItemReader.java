package com.example.BatchProcessor.reader;

import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.annotation.BeforeStep;
import org.springframework.batch.item.ItemReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
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
    private final String apiUrl = "http://localhost:8080/batch/personas"; // Esto podría ser configurable.
    private List<T> items;
    private int nextIndex;
    private Class<T> type;

    // Constructor donde el tipo de objeto es pasado como parámetro
    public ApiItemReader(RestTemplateBuilder restTemplateBuilder) {
        this.restTemplate = restTemplateBuilder.build();
        this.items = new ArrayList<>();
        this.nextIndex = 0;
    }

    @BeforeStep
    public void beforeStep(StepExecution stepExecution) throws ClassNotFoundException {
        // Obtener el parámetro 'entityClass' desde los JobParameters
        String entityClassName = stepExecution.getJobParameters().getString("entityClass");

        if (entityClassName != null) {
            // Cargar la clase usando Class.forName y asignarla al tipo generico
            Class<T> clazz = (Class<T>) Class.forName(entityClassName);
            this.type = clazz;
        } else {
            // Si no se pasa, manejar el error
            throw new IllegalArgumentException("Se debe proporcionar el parámetro 'entityClass'");
        }
    }

    @Override
    public T read() {
        if (items.isEmpty()) {
            // Llamada a la API para obtener los datos y convertirlos al tipo genérico
            ResponseEntity<T[]> response = restTemplate.getForEntity(apiUrl, (Class<T[]>) type.arrayType());
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                items = Arrays.asList(response.getBody());
            } else {
                // Manejo de errores si no se puede obtener los datos de la API
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
