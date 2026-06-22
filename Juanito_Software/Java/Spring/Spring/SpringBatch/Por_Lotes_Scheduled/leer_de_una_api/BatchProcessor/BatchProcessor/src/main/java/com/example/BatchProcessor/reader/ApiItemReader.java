package com.example.BatchProcessor.reader;

import com.example.BatchProcessor.model.Persona;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;


/**
 * Lector de archivo CSV que lee los registros de un archivo y los mapea a objetos FileRecord.
 * Esta clase es utilizada por Spring Batch para leer datos de archivos CSV y procesarlos por lotes.
 */
@Component
public class ApiItemReader implements ItemReader<Persona> {

    private final RestTemplate restTemplate;
    private final String apiUrl = "http://localhost:8080/batch/personas";
    private List<Persona> personas;
    private int nextIndex;

    public ApiItemReader(RestTemplateBuilder restTemplateBuilder) {
        this.restTemplate = restTemplateBuilder.build();
        this.personas = new ArrayList<>();
        this.nextIndex = 0;
    }

    @Override
    public Persona read() {
        if (personas.isEmpty()) {
            ResponseEntity<Persona[]> response = restTemplate.getForEntity(apiUrl, Persona[].class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                personas = Arrays.asList(response.getBody());
            }
        }

        if (nextIndex < personas.size()) {
            return personas.get(nextIndex++);
        } else {
            return null; // Indica el final de los datos
        }
    }
}
