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
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Ruta base de datos → CSV.
 *
 * <p>Es la primera vez que un test ejercita {@code databaseItemReader}. Merece
 * la pena saber qué se está poniendo a prueba además de la ruta: ese bean se
 * declara en {@code BatchConfig} con un parámetro
 * {@code @Value("#{jobParameters['entityClass']}")} pero **sin** {@code @StepScope},
 * mientras que la clase {@code DatabaseItemReader} sí lo lleva. Las expresiones
 * que leen {@code jobParameters} necesitan ámbito de paso para resolverse, así
 * que aquí se verá si esa combinación funciona o si la ruta estaba rota.
 *
 * <p>Los datos se siembran con el repositorio en lugar de depender de otro job,
 * para que un fallo señale a esta ruta y no a la de CSV a base de datos.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = "csv.output.file.path=target/test-output/bd-a-csv.csv")
class JobDatabaseACsvTest {

    private static final Path SALIDA = Path.of("target", "test-output", "bd-a-csv.csv");

    @Autowired
    private BatchController controlador;

    @Autowired
    private GenericRepository<GenericEntity, Long> repositorio;

    @Test
    @DisplayName("Lo que hay en la tabla acaba en el CSV de salida")
    void loQueEstaEnLaBaseDeDatosSeExportaACsv() throws IOException {
        Files.createDirectories(SALIDA.getParent());
        Files.deleteIfExists(SALIDA);

        repositorio.deleteAll();
        repositorio.save(new GenericEntity(null, "Primero"));
        repositorio.save(new GenericEntity(null, "Segundo"));
        repositorio.save(new GenericEntity(null, "Tercero"));

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "databaseItemReader",
                "processor", "genericProcessor",
                "writer", "csvItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado. Si es por el parámetro entityClass sin "
                        + "@StepScope, el detalle está en el log del test");

        assertTrue(Files.exists(SALIDA), "Deberia haberse creado el CSV de salida");

        List<String> lineas = Files.readAllLines(SALIDA);

        assertEquals(4, lineas.size(), "Una cabecera mas las tres filas sembradas");
        assertEquals("id,data", lineas.get(0));

        String contenido = String.join("\n", lineas);
        assertTrue(contenido.contains("Primero"), "Falta la primera fila: " + contenido);
        assertTrue(contenido.contains("Segundo"), "Falta la segunda fila: " + contenido);
        assertTrue(contenido.contains("Tercero"), "Falta la tercera fila: " + contenido);
    }
}
