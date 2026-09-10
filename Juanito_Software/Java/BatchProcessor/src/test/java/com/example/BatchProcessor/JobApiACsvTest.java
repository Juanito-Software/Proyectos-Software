package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
import com.example.BatchProcessor.reader.ApiItemReader;
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

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.client.ExpectedCount.once;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 * Ruta API → CSV.
 *
 * <p>Esta ruta estuvo mucho tiempo marcada como cubierta cuando no lo estaba.
 * Habia un test del lector ({@code ApiItemReaderTest}) y varios del escritor de
 * CSV, y de ahi se dedujo que la combinacion funcionaba. Deducir no es probar:
 * lo que ninguno de los dos ejercitaba es el paso completo, que es donde vive
 * el {@code genericProcessor} y donde el tipo que devuelve el lector tiene que
 * encajar con lo que el escritor sabe serializar.
 *
 * <p>Se usa {@code Persona} y no {@code GenericEntity} a proposito: tres campos
 * en lugar de dos, y una entidad que no hereda de nada. Asi la cabecera del CSV
 * de salida dice algo — si el escritor perdiera un campo por el camino, dos
 * columnas podrian colar, tres no.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = {
        "entityClass=com.example.BatchProcessor.model.Persona",
        "apiToReadUrl=http://api-origen/personas",
        "csv.output.file.path=target/test-output/api-a-csv.csv"
})
class JobApiACsvTest {

    private static final Path SALIDA = Path.of("target", "test-output", "api-a-csv.csv");

    private static final String RESPUESTA_ORIGEN = """
            [
              {"personaId": 1, "nombreCompleto": "Juan Perez", "empleo": "Desarrollador"},
              {"personaId": 2, "nombreCompleto": "Ana Garcia", "empleo": "Analista"},
              {"personaId": 3, "nombreCompleto": "Luis Ortega", "empleo": "Disenador"}
            ]
            """;

    @Autowired
    private BatchController controlador;

    @Autowired
    private ApiItemReader<Object> lector;

    @Test
    @DisplayName("Lo que devuelve la API acaba en el CSV de salida, con sus tres columnas")
    void loLeidoDeLaApiSeEscribeEnCsv() throws IOException {
        // El escritor añade al final del fichero en vez de sobrescribir, asi que
        // un fichero de una ejecucion anterior falsearia el recuento de lineas.
        Files.createDirectories(SALIDA.getParent());
        Files.deleteIfExists(SALIDA);

        RestTemplate clienteLector = (RestTemplate) ReflectionTestUtils.getField(lector, "restTemplate");
        MockRestServiceServer origen = MockRestServiceServer.bindTo(clienteLector).build();
        origen.expect(once(), requestTo("http://api-origen/personas"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(RESPUESTA_ORIGEN, MediaType.APPLICATION_JSON));

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "apiItemReader",
                "processor", "genericProcessor",
                "writer", "csvItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado; el motivo esta en el log del test");

        origen.verify();

        assertTrue(Files.exists(SALIDA), "Deberia haberse creado el CSV de salida");

        List<String> lineas = Files.readAllLines(SALIDA);

        assertEquals(4, lineas.size(), "Una cabecera mas las tres personas");
        assertEquals("personaId,nombreCompleto,empleo", lineas.get(0),
                "Las columnas salen en el orden de declaracion de la entidad");

        String contenido = String.join("\n", lineas);
        assertTrue(contenido.contains("Juan Perez"), "Falta la primera persona: " + contenido);
        assertTrue(contenido.contains("Ana Garcia"), "Falta la segunda persona: " + contenido);
        assertTrue(contenido.contains("Luis Ortega"), "Falta la tercera persona: " + contenido);
        assertTrue(contenido.contains("Disenador"),
                "Falta el tercer campo: si solo se escribieran personaId y "
                        + "nombreCompleto el recuento de lineas no lo detectaria");
    }
}
