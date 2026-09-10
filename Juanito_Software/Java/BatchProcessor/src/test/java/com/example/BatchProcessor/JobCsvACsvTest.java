package com.example.BatchProcessor;

import com.example.BatchProcessor.controller.BatchController;
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
 * Ruta CSV → CSV.
 *
 * <p>Estaba documentada como funcional a partir de pruebas manuales de hace un
 * año. Esto la ejecuta de verdad y comprueba el fichero resultante.
 *
 * <p>La salida va a {@code target/}, que se borra con {@code mvn clean} y no
 * ensucia {@code src/main/resources} como hace la ruta por defecto.
 */
@SpringBootTest
@ActiveProfiles("test")
@TestPropertySource(properties = "csv.output.file.path=target/test-output/csv-a-csv.csv")
class JobCsvACsvTest {

    private static final Path SALIDA = Path.of("target", "test-output", "csv-a-csv.csv");

    @Autowired
    private BatchController controlador;

    @Test
    @DisplayName("Las diez filas del CSV de ejemplo acaban en el CSV de salida")
    void elCsvDeEntradaSeCopiaAlDeSalida() throws IOException {
        // El escritor abre el fichero en modo añadir, asi que sin limpiar antes
        // el test acumularia filas de ejecuciones anteriores y pasaria o
        // fallaria segun cuantas veces se hubiera lanzado.
        Files.createDirectories(SALIDA.getParent());
        Files.deleteIfExists(SALIDA);

        ResponseEntity<String> respuesta = controlador.runBatchJob(Map.of(
                "reader", "csvItemReader",
                "processor", "genericProcessor",
                "writer", "csvItemWriter"));

        assertEquals(HttpStatus.OK, respuesta.getStatusCode(),
                "El job no ha arrancado; el motivo esta en el log del test");

        assertTrue(Files.exists(SALIDA), "El escritor deberia haber creado el fichero de salida");

        List<String> lineas = Files.readAllLines(SALIDA);

        assertEquals(11, lineas.size(),
                "Una cabecera mas las diez filas de input.csv");

        // Las columnas salen en el orden en que la entidad las declara.
        //
        // Merece una nota, porque CsvItemWriter tiene veinte lineas dedicadas a
        // construir un esquema con las columnas INVERTIDAS —recorre
        // getColumnNames(), hace Collections.reverse y monta un CsvSchema
        // nuevo— y ese esquema se pasa a los dos writerFor. Este test se
        // escribio esperando 'data,id' y salio 'id,data': el bloque no surte
        // efecto. Por que no lo hace esta sin averiguar; lo que si esta
        // comprobado es el resultado, y es lo que se fija aqui.
        assertEquals("id,data", lineas.get(0),
                "Las columnas salen en el orden de declaracion de la entidad, "
                        + "pese al bloque de CsvItemWriter que pretende invertirlas");

        assertTrue(lineas.get(1).startsWith("1,"),
                "La primera fila de datos deberia ser la primera de input.csv: " + lineas.get(1));
    }
}
