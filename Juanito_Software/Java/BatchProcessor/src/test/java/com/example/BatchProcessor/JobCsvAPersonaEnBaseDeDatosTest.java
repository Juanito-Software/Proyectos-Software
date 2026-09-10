package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Escribir en base de datos una entidad que NO extiende {@code GenericEntity}.
 *
 * <p>Esto no se podia hacer. El escritor era un
 * {@code ManualItemWriter<T extends GenericEntity>} que guardaba con un
 * repositorio de Spring Data, y esa firma dejaba fuera a cualquier
 * {@code @Entity} independiente. {@code Persona} lo es, asi que podia ir a CSV
 * y a la API pero no a base de datos.
 *
 * <p>Al cambiar el bean por un {@code JpaItemWriter}, que persiste via
 * {@code EntityManager}, la restriccion desaparece. Este test existe para
 * demostrarlo, no para cubrir una funcionalidad nueva: si alguien vuelve a
 * atar el escritor a una jerarquia concreta, esto se pone en rojo.
 *
 * <p>Las propiedades se sobrescriben aqui en lugar de en el perfil porque son
 * especificas de este caso: el resto de tests deben seguir ejecutando la
 * configuracion real del proyecto.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = {
        "entityClass=com.example.BatchProcessor.model.Persona",
        "csv.file.path=persona-ejemplo.csv"
})
class JobCsvAPersonaEnBaseDeDatosTest {

    @Autowired
    private BatchController controlador;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    @DisplayName("Una entidad que no hereda de GenericEntity ya puede guardarse en base de datos")
    void personaSeGuardaEnBaseDeDatos() {
        jdbcTemplate.execute("DELETE FROM persona");

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "csvItemReader",
                "processor", "genericProcessor",
                "writer", "databaseItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado. El motivo esta en el log del test, "
                        + "porque el controlador no lo expone en la respuesta.");

        Integer guardadas = jdbcTemplate.queryForObject(
                "SELECT COUNT(*) FROM persona", Integer.class);

        assertEquals(3, guardadas,
                "Las tres filas del CSV de personas deberian estar en la tabla");
    }
}
