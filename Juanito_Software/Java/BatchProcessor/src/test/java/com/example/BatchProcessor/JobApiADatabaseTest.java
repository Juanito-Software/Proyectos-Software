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
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.client.ExpectedCount.once;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 * Ruta API → base de datos. La novena, y la ultima que quedaba sin recorrer
 * entera.
 *
 * <p>Es la combinacion que mas ha cambiado de las nueve, y por eso interesa
 * tenerla fijada. Hasta hace poco no podia funcionar por dos motivos a la vez:
 * el lector devolvia {@code LinkedHashMap} en lugar de entidades —el borrado de
 * tipos de {@code ParameterizedTypeReference<List<T>>}— y el escritor exigia
 * heredar de {@code GenericEntity}, cosa que {@code Persona} no hace. Se
 * arreglaron por separado; aqui se comprueba que los dos arreglos se sostienen
 * juntos.
 *
 * <p>No se afirma solo que haya tres filas: se lee una de ellas por su nombre.
 * Un lector que devolviera mapas y un escritor que los persistiera a medias
 * podrian dejar el recuento correcto y los campos vacios.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = {
        "entityClass=com.example.BatchProcessor.model.Persona",
        "apiToReadUrl=http://api-origen/personas"
})
class JobApiADatabaseTest {

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

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    @DisplayName("Lo que devuelve la API se guarda en la tabla, con sus campos")
    void loLeidoDeLaApiSeGuardaEnBaseDeDatos() {
        jdbcTemplate.execute("DELETE FROM persona");

        RestTemplate clienteLector = (RestTemplate) ReflectionTestUtils.getField(lector, "restTemplate");
        MockRestServiceServer origen = MockRestServiceServer.bindTo(clienteLector).build();
        origen.expect(once(), requestTo("http://api-origen/personas"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(RESPUESTA_ORIGEN, MediaType.APPLICATION_JSON));

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "apiItemReader",
                "processor", "genericProcessor",
                "writer", "databaseItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado; el motivo esta en el log del test");

        origen.verify();

        Integer guardadas = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM persona", Integer.class);

        assertEquals(3, guardadas, "Las tres personas de la API deberian estar en la tabla");

        // No se nombra ninguna columna en el SQL, y no es pereza.
        //
        // Los campos de Persona -personaId, nombreCompleto- llevan mayusculas en
        // medio, y ahi H2 no perdona: los identificadores sin comillas los pasa a
        // mayusculas, asi que "WHERE personaId" acaba buscando PERSONAID y falla
        // con "bad SQL grammar". Entrecomillar tampoco sirve, porque exige
        // acertar la capitalizacion exacta con la que Hibernate creo la columna,
        // que depende del dialecto.
        //
        // Un SELECT * usa solo el nombre de la tabla, que es de una sola palabra,
        // y la fila se busca por su contenido. Asi la comprobacion es sobre los
        // datos y no sobre como capitalice el motor de turno.
        List<Map<String, Object>> filas = jdbcTemplate.queryForList("SELECT * FROM persona");

        Map<String, Object> ana = filas.stream()
                .filter(fila -> fila.containsValue("Ana Garcia"))
                .findFirst()
                .orElseThrow(() -> new AssertionError(
                        "No se ha guardado ninguna fila con 'Ana Garcia'. Filas: " + filas));

        assertTrue(ana.containsValue("Analista"),
                "La fila de Ana esta pero le falta el empleo, asi que los campos "
                        + "no han viajado enteros: el lector podria estar "
                        + "devolviendo mapas otra vez. Fila: " + ana);
    }
}
