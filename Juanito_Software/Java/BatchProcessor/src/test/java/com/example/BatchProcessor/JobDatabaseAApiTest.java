package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.repository.GenericRepository;
import com.example.BatchProcessor.writer.ApiItemWriter;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
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
 * Ruta base de datos → API.
 *
 * <p>Junta las dos piezas que mas problemas han dado: el lector de base de
 * datos, que estuvo roto por una colision de nombres de bean, y el escritor de
 * API, que multiplicaba los envios. Ninguna de las dos se habia ejecutado nunca
 * en un test hasta hoy.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = "apiToWriteUrl=http://api-simulada/guardar")
class JobDatabaseAApiTest {

    @Autowired
    private BatchController controlador;

    @Autowired
    private GenericRepository<GenericEntity, Long> repositorio;

    @Autowired
    private ApiItemWriter<Object> escritor;

    @Test
    @DisplayName("Las filas de la tabla se envian a la API en una sola peticion")
    void loQueEstaEnLaBaseDeDatosSeEnviaALaApi() {
        repositorio.deleteAll();
        repositorio.save(new GenericEntity(null, "Primero"));
        repositorio.save(new GenericEntity(null, "Segundo"));
        repositorio.save(new GenericEntity(null, "Tercero"));

        RestTemplate restTemplate = (RestTemplate) ReflectionTestUtils.getField(escritor, "restTemplate");
        MockRestServiceServer servidor = MockRestServiceServer.bindTo(restTemplate).build();

        servidor.expect(once(), requestTo("http://api-simulada/guardar"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(jsonPath("$.length()").value(3))
                .andRespond(withSuccess());

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "databaseItemReader",
                "processor", "genericProcessor",
                "writer", "apiItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado; el motivo esta en el log del test");

        servidor.verify();
    }
}
