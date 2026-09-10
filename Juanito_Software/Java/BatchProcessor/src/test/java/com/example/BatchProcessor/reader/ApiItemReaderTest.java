package com.example.BatchProcessor.reader;

import com.example.BatchProcessor.model.Persona;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.test.MetaDataInstanceFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

/**
 * Lo que devuelve el lector de API: entidades, no mapas.
 *
 * <p>Esta es la comprobacion que decide si el arreglo del borrado de tipos se
 * sostiene. Antes, {@code ParameterizedTypeReference<List<T>>} perdia el tipo
 * al compilar y Jackson devolvia {@code LinkedHashMap}; por eso las rutas que
 * leian de la API obligaban a usar un procesador especifico que rehiciera la
 * entidad campo a campo.
 *
 * <p>Si el primer test pasa, ese procesador deja de ser necesario para mapear
 * —seguiria haciendo falta solo cuando la API devuelva una forma distinta de la
 * entidad, que es mapeo de verdad—.
 *
 * <p>La API se simula con {@code MockRestServiceServer}. No hay servidor ni
 * red: se intercepta el {@code RestTemplate} que el lector construyo en su
 * constructor.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = "apiToReadUrl=http://api-simulada/personas")
class ApiItemReaderTest {

    private static final String RESPUESTA_JSON = """
            [
              {"personaId": 1, "nombreCompleto": "Juan Perez", "empleo": "Desarrollador"},
              {"personaId": 2, "nombreCompleto": "Ana Garcia", "empleo": "Analista"}
            ]
            """;

    @Autowired
    private ApiItemReader<Persona> lector;

    /** Intercepta el RestTemplate interno del lector y le prepara la respuesta. */
    private MockRestServiceServer simularApi() {
        RestTemplate restTemplate = (RestTemplate) ReflectionTestUtils.getField(lector, "restTemplate");
        MockRestServiceServer servidor = MockRestServiceServer.bindTo(restTemplate).build();

        servidor.expect(requestTo("http://api-simulada/personas"))
                .andExpect(method(org.springframework.http.HttpMethod.GET))
                .andRespond(withSuccess(RESPUESTA_JSON, MediaType.APPLICATION_JSON));

        return servidor;
    }

    private StepExecution pasoCon(String nombreDeClase) {
        JobParameters parametros = new JobParametersBuilder()
                .addString("entityClass", nombreDeClase)
                .toJobParameters();
        return MetaDataInstanceFactory.createStepExecution(parametros);
    }

    @Test
    @DisplayName("La respuesta se convierte en la entidad configurada, no en un mapa")
    void devuelveEntidadesYNoMapas() {
        simularApi();
        lector.beforeStep(pasoCon(Persona.class.getName()));

        Object primero = lector.read();

        assertInstanceOf(Persona.class, primero,
                "Si esto falla y llega un LinkedHashMap, el borrado de tipos sigue sin resolverse");

        Persona persona = (Persona) primero;
        assertEquals("Juan Perez", persona.getNombreCompleto());
        assertEquals(1L, persona.getPersonaId().longValue(),
                "El identificador debe llegar como Long, sin las conversiones a mano "
                        + "que hacia PersonaItemProcessor con un cast a Integer");
    }

    @Test
    @DisplayName("Se leen todos los registros y luego se devuelve null")
    void recorreTodosLosRegistros() {
        simularApi();
        lector.beforeStep(pasoCon(Persona.class.getName()));

        assertEquals("Juan Perez", ((Persona) lector.read()).getNombreCompleto());
        assertEquals("Ana Garcia", ((Persona) lector.read()).getNombreCompleto());
        assertNull(lector.read(), "Agotada la lista, read() debe devolver null para cerrar el paso");
    }

    @Test
    @DisplayName("Un segundo paso vuelve a empezar desde el principio")
    void elEstadoSeReiniciaEntrePasos() {
        // El lector es un singleton. Sin reiniciar items y nextIndex en
        // beforeStep, el segundo job del mismo arranque encontraria el indice al
        // final de la lista anterior y leeria cero registros — terminando en
        // COMPLETED sin haber procesado nada, que es el peor fallo posible.
        simularApi();
        lector.beforeStep(pasoCon(Persona.class.getName()));
        lector.read();
        lector.read();
        assertNull(lector.read());

        simularApi();
        lector.beforeStep(pasoCon(Persona.class.getName()));

        assertEquals("Juan Perez", ((Persona) lector.read()).getNombreCompleto(),
                "Tras un beforeStep nuevo, el lector debe empezar otra vez por el primer registro");
    }
}
