package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.repository.GenericRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

import javax.sql.DataSource;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Ruta base de datos → base de datos: la que faltaba.
 *
 * <p>Lo que hace que este test valga algo es que las dos bases son
 * **distintas**: el perfil de test apunta la principal a {@code batchprocessor}
 * y la segunda a {@code batchprocessor_destino}. Si apuntaran a la misma, el job
 * leería y escribiría en el mismo sitio y el test pasaría sin demostrar nada.
 *
 * <p>Se comprueban las dos mitades: que las filas aparecen en el destino y que
 * **siguen** en el origen. Un job que moviera en vez de copiar también dejaría
 * las tres filas en el destino.
 */
@SpringBootTest
@ActiveProfiles("test")
class JobDatabaseADatabaseTest {

    @Autowired
    private BatchController controlador;

    @Autowired
    private GenericRepository<GenericEntity, Long> repositorioOrigen;

    @Autowired
    @Qualifier("secondDataSource")
    private DataSource segundaBaseDeDatos;

    @Test
    @DisplayName("Las filas se copian de una base de datos a la otra")
    void lasFilasViajanDeUnaBaseALaOtra() {
        JdbcTemplate destino = new JdbcTemplate(segundaBaseDeDatos);

        repositorioOrigen.deleteAll();
        repositorioOrigen.save(new GenericEntity(null, "Primero"));
        repositorioOrigen.save(new GenericEntity(null, "Segundo"));
        repositorioOrigen.save(new GenericEntity(null, "Tercero"));

        destino.execute("DELETE FROM genericentity");

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "databaseItemReader",
                "processor", "genericProcessor",
                "writer", "secondDatabaseItemWriter",
                "transactionManager", "secondTransactionManager"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado. Si es por el emparejamiento de escritor "
                        + "y gestor de transacciones, el detalle esta en el log del test");

        Integer enDestino = destino.queryForObject(
                "SELECT COUNT(*) FROM genericentity", Integer.class);

        assertEquals(3, enDestino,
                "Las tres filas deberian estar en la segunda base de datos");

        assertEquals(3, repositorioOrigen.count(),
                "Y deberian seguir en la primera: esto copia, no mueve");
    }
}
