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

    /**
     * Envía el bloque completo en una sola petición.
     *
     * <p>Aquí había un bucle {@code for (T item : chunk)} que, en cada vuelta,
     * hacía un POST con la lista **entera**. Un bloque de diez registros
     * generaba diez peticiones de diez registros cada una: la API receptora
     * recibía cien. Y el job terminaba en COMPLETED, porque las diez respuestas
     * eran 200.
     *
     * <p>Lo destapó {@code JobCsvAApiTest} al contar peticiones en lugar de
     * mirar solo el estado final del job.
     */
    @Override
    public void write(Chunk<? extends T> chunk) throws Exception {
        List<? extends T> items = chunk.getItems();

        if (items.isEmpty()) {
            return;
        }

        try {
            ResponseEntity<Void> response = restTemplate.postForEntity(apiUrl, items, Void.class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                throw new RuntimeException("Error al enviar datos a la API: " + response.getStatusCode());
            }
        } catch (Exception e) {
            // El detalle va al log de Spring Batch, no al mensaje: la version
            // anterior concatenaba el item en la excepcion, que es como los
            // datos de negocio acaban en un registro de errores.
            throw new RuntimeException(
                    "Error al enviar a la API el bloque de " + items.size() + " registros", e);
        }
    }
}

