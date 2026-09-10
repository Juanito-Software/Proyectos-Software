package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
import com.example.BatchProcessor.reader.ApiItemReader;
import com.example.BatchProcessor.writer.ApiItemWriter;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.client.ExpectedCount.once;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.jsonPath;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 * Ruta API → API.
 *
 * <p>Es la unica de las tres rutas de API que nunca necesito un procesador
 * especifico, porque los datos entraban y salian sin persistirse. Ahora que el
 * lector devuelve entidades en vez de mapas, sigue sin necesitarlo, pero por
 * otra razon: {@code genericProcessor} vale para todas.
 *
 * <p>El lector y el escritor construyen cada uno su propio {@code RestTemplate},
 * asi que hacen falta dos servidores simulados, uno por cada cliente.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = {
        "entityClass=com.example.BatchProcessor.model.Persona",
        "apiToReadUrl=http://api-origen/personas",
        "apiToWriteUrl=http://api-destino/personas"
})
class JobApiAApiTest {

    private static final String RESPUESTA_ORIGEN = """
            [
              {"personaId": 1, "nombreCompleto": "Juan Perez", "empleo": "Desarrollador"},
              {"personaId": 2, "nombreCompleto": "Ana Garcia", "empleo": "Analista"}
            ]
            """;

    @Autowired
    private BatchController controlador;

    @Autowired
    private ApiItemReader<Object> lector;

    @Autowired
    private ApiItemWriter<Object> escritor;

    @Test
    @DisplayName("Lo que devuelve una API se reenvia a la otra, una sola vez y completo")
    void loLeidoDeUnaApiSeEnviaALaOtra() {
        RestTemplate clienteLector = (RestTemplate) ReflectionTestUtils.getField(lector, "restTemplate");
        MockRestServiceServer origen = MockRestServiceServer.bindTo(clienteLector).build();
        origen.expect(once(), requestTo("http://api-origen/personas"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(RESPUESTA_ORIGEN, MediaType.APPLICATION_JSON));

        RestTemplate clienteEscritor = (RestTemplate) ReflectionTestUtils.getField(escritor, "restTemplate");
        MockRestServiceServer destino = MockRestServiceServer.bindTo(clienteEscritor).build();
        destino.expect(once(), requestTo("http://api-destino/personas"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].nombreCompleto").value("Juan Perez"))
                .andRespond(withSuccess());

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "apiItemReader",
                "processor", "genericProcessor",
                "writer", "apiItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado; el motivo esta en el log del test");

        origen.verify();
        destino.verify();
    }
}
