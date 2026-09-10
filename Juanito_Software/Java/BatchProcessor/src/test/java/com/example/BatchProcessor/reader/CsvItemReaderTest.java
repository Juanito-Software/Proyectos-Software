package com.example.BatchProcessor.reader;

import com.example.BatchProcessor.model.GenericEntity;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.StepExecution;
import org.springframework.batch.test.MetaDataInstanceFactory;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Resolucion de la entidad por reflexion y validacion de cabeceras del CSV.
 *
 * <p>Son las dos piezas que hacen generico a este lector: la entidad no se
 * conoce al compilar, llega como parametro del job y se resuelve con
 * {@code Class.forName}; y las cabeceras del fichero se contrastan contra los
 * campos declarados de esa entidad antes de leer una sola fila.
 *
 * <p>Se prueban sin levantar el contexto de Spring y sin base de datos. El
 * unico apaño es {@code ReflectionTestUtils} para rellenar {@code filePath},
 * que es un campo privado con {@code @Value} y no tiene setter: en produccion
 * lo inyecta Spring, aqui se pone a mano. Es preferible a arrancar la
 * aplicacion entera para probar una validacion de cadenas.
 */
class CsvItemReaderTest {

    /** Construye el lector con la ruta de CSV que necesite cada caso. */
    private CsvItemReader<GenericEntity> lectorCon(String rutaCsv) {
        CsvItemReader<GenericEntity> lector = new CsvItemReader<>();
        ReflectionTestUtils.setField(lector, "filePath", rutaCsv);
        return lector;
    }

    /** StepExecution con el parametro entityClass que espera beforeStep. */
    private StepExecution pasoCon(String nombreDeClase) {
        JobParameters parametros = new JobParametersBuilder()
                .addString("entityClass", nombreDeClase)
                .toJobParameters();
        return MetaDataInstanceFactory.createStepExecution(parametros);
    }

    @Test
    @DisplayName("Sin el parametro entityClass no se puede resolver la entidad y se rechaza")
    void sinParametroEntityClass() {
        CsvItemReader<GenericEntity> lector = lectorCon("entidad-cabeceras-validas.csv");
        StepExecution paso = MetaDataInstanceFactory.createStepExecution(new JobParameters());

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, () -> lector.beforeStep(paso));

        assertTrue(error.getMessage().contains("entityClass"),
                "El mensaje debe nombrar el parametro que falta: " + error.getMessage());
    }

    @Test
    @DisplayName("Una clase inexistente falla al arrancar el paso, no al leer la primera fila")
    void claseInexistente() {
        CsvItemReader<GenericEntity> lector = lectorCon("entidad-cabeceras-validas.csv");
        StepExecution paso = pasoCon("com.example.BatchProcessor.model.NoExiste");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, () -> lector.beforeStep(paso));

        assertTrue(error.getMessage().contains("Class not found"),
                "Debe distinguirse de otros fallos de configuracion: " + error.getMessage());
        assertTrue(error.getCause() instanceof ClassNotFoundException,
                "La causa original no debe perderse");
    }

    @Test
    @DisplayName("Con una entidad valida y cabeceras que coinciden, el paso arranca")
    void cabecerasQueCoinciden() {
        CsvItemReader<GenericEntity> lector = lectorCon("entidad-cabeceras-validas.csv");
        StepExecution paso = pasoCon(GenericEntity.class.getName());

        assertDoesNotThrow(() -> lector.beforeStep(paso));
    }

    @Test
    @DisplayName("El input.csv que trae el repositorio es valido para la entidad configurada")
    void elCsvDeEjemploEsCoherenteConLaConfiguracionPorDefecto() {
        // Este test vigila una incoherencia que existio: application.properties
        // traia entityClass=...model.Persona mientras input.csv tiene cabeceras
        // 'id,data', que son los campos de GenericEntity. Quien clonaba el
        // repositorio y lanzaba el ejemplo se comia un "Unknown header in CSV
        // file: id".
        //
        // Persona se retiro y el valor por defecto pasa a GenericEntity. Esto
        // comprueba que el fichero de ejemplo y la entidad por defecto siguen
        // encajando, para que no vuelva a separarse en silencio.
        CsvItemReader<GenericEntity> lector = lectorCon("input.csv");
        StepExecution paso = pasoCon(GenericEntity.class.getName());

        assertDoesNotThrow(() -> lector.beforeStep(paso),
                "El input.csv del repositorio debe poder leerse con la entidad configurada por defecto");
    }

    @Test
    @DisplayName("Una cabecera que no es campo de la entidad se rechaza antes de leer datos")
    void cabeceraDesconocida() {
        // GenericEntity no tiene ningun campo 'telefono'. Sin esta comprobacion
        // el fallo aparecería mas tarde y peor: al mapear filas, con un mensaje
        // sobre propiedades de un bean en vez de sobre el CSV.
        CsvItemReader<GenericEntity> lector = lectorCon("entidad-cabecera-desconocida.csv");
        StepExecution paso = pasoCon(GenericEntity.class.getName());

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, () -> lector.beforeStep(paso));

        assertTrue(error.getMessage().contains("Unknown header"),
                "Debe decir que la cabecera es desconocida: " + error.getMessage());
        assertTrue(error.getMessage().contains("telefono"),
                "Y debe decir cual, o no sirve para depurar: " + error.getMessage());
    }

    @Test
    @DisplayName("Un CSV sin cabeceras se rechaza con un mensaje propio")
    void csvSinCabeceras() {
        CsvItemReader<GenericEntity> lector = lectorCon("csv-sin-cabeceras.csv");
        StepExecution paso = pasoCon(GenericEntity.class.getName());

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, () -> lector.beforeStep(paso));

        assertTrue(error.getMessage().contains("does not contain headers"),
                "Un fichero vacio no es lo mismo que uno con cabeceras malas: " + error.getMessage());
    }
}
