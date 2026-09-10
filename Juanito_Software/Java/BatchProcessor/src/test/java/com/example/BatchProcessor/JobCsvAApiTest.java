package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
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
 * Ruta CSV → API.
 *
 * <p>Comprueba lo que se envía, no solo que el job termine en COMPLETED. Un
 * escritor que mande los datos mal seguiría dando COMPLETED mientras la API
 * respondiera 200, así que contar peticiones y contenido es lo único que
 * distingue «funciona» de «no ha explotado».
 *
 * <p>El bloque de Spring Batch es de 10 y {@code input.csv} tiene 10 filas, así
 * que lo correcto es **una** petición POST con los diez registros dentro.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = "apiToWriteUrl=http://api-simulada/guardar")
class JobCsvAApiTest {

    @Autowired
    private BatchController controlador;

    @Autowired
    private ApiItemWriter<Object> escritor;

    @Test
    @DisplayName("El bloque entero viaja en una sola petición, sin repetirse")
    void elBloqueSeEnviaUnaVezConTodosLosRegistros() {
        RestTemplate restTemplate = (RestTemplate) ReflectionTestUtils.getField(escritor, "restTemplate");
        MockRestServiceServer servidor = MockRestServiceServer.bindTo(restTemplate).build();

        servidor.expect(once(), requestTo("http://api-simulada/guardar"))
                .andExpect(method(HttpMethod.POST))
                .andExpect(jsonPath("$.length()").value(10))
                .andRespond(withSuccess());

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "csvItemReader",
                "processor", "genericProcessor",
                "writer", "apiItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado; el motivo esta en el log del test");

        // Falla si hubo mas peticiones de las esperadas, que es justo lo que
        // pasa cuando el escritor envia la lista completa una vez por cada
        // elemento del bloque.
        servidor.verify();
    }
}
