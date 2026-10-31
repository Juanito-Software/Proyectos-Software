package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.repository.GenericRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * El recorrido completo: CSV → procesador → base de datos.
 *
 * <p>Hasta ahora todo lo que se probaba era que el contexto arranca y que el
 * lector valida cabeceras. Nada comprobaba que la aplicación haga su trabajo,
 * que es mover datos de un sitio a otro. Este test lanza el job igual que lo
 * lanza el endpoint {@code /batch/run} y comprueba que las diez filas del
 * {@code input.csv} de ejemplo acaban en la base de datos.
 *
 * <p>Corre sobre H2 gracias al perfil de test, y el {@code JobLauncher} usa un
 * {@code SyncTaskExecutor}, asi que cuando la llamada vuelve el job ha
 * terminado: no hay esperas ni margen para inestabilidad.
 *
 * <p>Nota sobre el diagnostico: el controlador captura cualquier excepcion y
 * responde 500 con un mensaje generico, dejando el detalle en el log. Es lo
 * correcto de cara al exterior, pero significa que si este test falla hay que
 * mirar la salida de surefire para saber por que.
 */
@SpringBootTest
@ActiveProfiles("test")
class JobCsvADatabaseTest {

    @Autowired
    private BatchController controlador;

    @Autowired
    private GenericRepository<GenericEntity, Long> repositorio;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    @DisplayName("Las diez filas del CSV de ejemplo acaban guardadas en la base de datos")
    void elCsvDeEjemploAcabaEnLaBaseDeDatos() {
        repositorio.deleteAll();
        // deleteAll() vacia la tabla pero NO reinicia el contador IDENTITY.
        // El CSV trae ids 1..10 y JpaItemWriter hace merge: si otro test de la
        // misma JVM ya inserto filas (p. ej. 3, contador en 4), los ids 1..3 se
        // insertan como 4..6 y los ids 4..6 del CSV coinciden con ellas y se
        // ACTUALIZAN en vez de insertarse -> 7 filas. El resultado dependia del
        // orden de los tests (Surefire usa el del sistema de ficheros). Se
        // reinicia el contador para que el test no dependa de lo que corrio
        // antes. El problema de fondo (importar un CSV con ids sobre una tabla
        // con datos sobrescribe filas) queda anotado en MAINTENANCE.md.
        jdbcTemplate.execute("ALTER TABLE genericentity ALTER COLUMN id RESTART WITH 1");

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "csvItemReader",
                "processor", "genericProcessor",
                "writer", "databaseItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado. El motivo esta en el log del test, "
                        + "porque el controlador no lo expone en la respuesta.");

        assertEquals(10, repositorio.count(),
                "El CSV de ejemplo tiene diez filas; deberian estar todas en la base de datos.");
    }
}
