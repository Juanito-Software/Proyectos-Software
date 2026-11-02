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
 * Escritor que envía cada chunk a una API REST con un POST.
 *
 * <p>El cuerpo es un array JSON con los elementos del chunk (hasta 10, el
 * tamaño de chunk del controlador), serializados con los campos de la entidad.
 * La API receptora debe aceptar una lista, como la de ejemplo en
 * {@code apiToWriteUrl}.
 *
 * <p>No reintenta: si una petición falla, el paso falla y el job termina en
 * {@code FAILED}. Los chunks ya enviados antes del fallo no se deshacen, porque
 * la transacción del paso no abarca a la API remota.
 *
 * @param <T> tipo de la entidad
 */
@Component
public class ApiItemWriter<T> implements ItemWriter<T> {

    /** Cliente HTTP construido con la configuración de Spring Boot. */
    private final RestTemplate restTemplate;

    // URL de la API donde se enviarán los datos (propiedad apiToWriteUrl)
    private String apiUrl;

    /**
     * @param restTemplateBuilder constructor de {@code RestTemplate}
     * @param apiUrl              URL de escritura ({@code apiToWriteUrl})
     */
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
     *
     * @param chunk elementos a enviar; si está vacío no se hace ninguna petición
     * @throws RuntimeException si la API responde con un código no 2xx o la
     *                          petición falla (la causa original va encadenada)
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

