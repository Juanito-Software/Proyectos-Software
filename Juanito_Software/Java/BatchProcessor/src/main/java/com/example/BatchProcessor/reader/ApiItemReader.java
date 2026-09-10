package com.example.BatchProcessor.reader;

import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.StepExecutionListener;
import org.springframework.batch.item.ItemReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

/**
 * Lee registros de una API REST y los entrega ya convertidos en la entidad
 * configurada.
 *
 * <p>── Por que no se usa ParameterizedTypeReference ────────────────────────
 *
 * <p>La version anterior pedia la respuesta con
 * {@code ParameterizedTypeReference<List<T>>}. Ese {@code T} es una variable de
 * tipo y Java la borra al compilar, asi que en ejecucion no habia ninguna clase
 * concreta que darle a Jackson y la respuesta llegaba como una lista de
 * {@code LinkedHashMap}. De ahi venia la obligacion de usar un procesador
 * especifico por entidad para convertir esos mapas: no era mapeo de negocio,
 * era compensar el borrado de tipos.
 *
 * <p>Aqui se resuelve en el sitio correcto. La clase concreta ya se conoce en
 * ejecucion —llega como parametro del job y se resuelve con
 * {@code Class.forName}—, asi que se construye con ella el tipo que espera
 * Jackson y la deserializacion produce entidades directamente. Con eso
 * {@code genericProcessor} basta para cualquier entidad.
 *
 * <p>── Por que implementa StepExecutionListener ──────────────────────────
 *
 * <p>Antes la clase solo llevaba la anotacion {@code @BeforeStep} sin
 * implementar ninguna interfaz de escucha. Spring Batch registra
 * automaticamente como oyentes los lectores que implementan
 * {@code StepExecutionListener}, que es lo que hace {@code CsvItemReader}; con
 * la anotacion suelta no hay garantia de que el metodo llegue a llamarse. Daba
 * igual mientras el campo que rellenaba no se usara para nada, pero ahora la
 * deserializacion depende de el.
 */
@Component
public class ApiItemReader<T> implements ItemReader<T>, StepExecutionListener {

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final String apiUrl;

    private List<T> items = new ArrayList<>();
    private int nextIndex = 0;
    private Class<T> entityType;

    public ApiItemReader(RestTemplateBuilder restTemplateBuilder,
                         ObjectMapper objectMapper,
                         @Value("${apiToReadUrl}") String apiUrl) {
        this.restTemplate = restTemplateBuilder.build();
        this.objectMapper = objectMapper;
        this.apiUrl = apiUrl;
    }

    /**
     * Resuelve la entidad y deja el lector como recien puesto.
     *
     * <p>El reinicio de {@code items} y {@code nextIndex} no es adorno: el bean
     * es un singleton, asi que sin el, un segundo job en el mismo arranque
     * encontraria el indice al final de la lista anterior y no leeria nada. No
     * fallaria: devolveria cero elementos y el job terminaria en COMPLETED.
     */
    @Override
    @SuppressWarnings("unchecked")
    public void beforeStep(StepExecution stepExecution) {
        String entityClassName = stepExecution.getJobParameters().getString("entityClass");

        if (entityClassName == null) {
            throw new IllegalArgumentException("Se debe proporcionar el parámetro 'entityClass'");
        }

        try {
            this.entityType = (Class<T>) Class.forName(entityClassName);
        } catch (ClassNotFoundException e) {
            throw new IllegalArgumentException("Class not found: " + entityClassName, e);
        }

        this.items = new ArrayList<>();
        this.nextIndex = 0;
    }

    @Override
    public T read() {
        if (items.isEmpty()) {
            items = descargar();
        }

        return nextIndex < items.size() ? items.get(nextIndex++) : null;
    }

    private List<T> descargar() {
        if (entityType == null) {
            throw new IllegalStateException(
                    "El lector no sabe a qué entidad convertir la respuesta. "
                            + "beforeStep no se ha ejecutado.");
        }

        ResponseEntity<String> respuesta =
                restTemplate.exchange(apiUrl, HttpMethod.GET, null, String.class);

        if (!respuesta.getStatusCode().is2xxSuccessful() || respuesta.getBody() == null) {
            throw new RuntimeException("Error al obtener datos de la API: " + respuesta.getStatusCode());
        }

        JavaType tipoLista = objectMapper.getTypeFactory()
                .constructCollectionType(List.class, entityType);

        try {
            return objectMapper.readValue(respuesta.getBody(), tipoLista);
        } catch (Exception e) {
            throw new RuntimeException(
                    "La respuesta de la API no se ha podido convertir en "
                            + entityType.getSimpleName(), e);
        }
    }
}
