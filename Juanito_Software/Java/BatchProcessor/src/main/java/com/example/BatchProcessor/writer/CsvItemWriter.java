package com.example.BatchProcessor.writer;

import com.fasterxml.jackson.dataformat.csv.CsvMapper;
import com.fasterxml.jackson.dataformat.csv.CsvSchema;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * Escritor que añade cada chunk al final de un fichero CSV.
 *
 * <p>Las columnas se deducen de la clase del primer elemento con Jackson CSV,
 * así que sirve para cualquier entidad sin configuración, y salen en el orden
 * en que la entidad declara sus campos. La cabecera solo se escribe si el
 * fichero no existe o está vacío.
 *
 * <p><b>Nunca vacía el fichero.</b> Escribe en modo <i>append</i>: lanzar el
 * mismo job dos veces deja las filas duplicadas. Si hace falta empezar de cero,
 * hay que borrar el fichero antes. La ruta ({@code csv.output.file.path}) es
 * relativa al directorio desde el que se arranca la aplicación, no al
 * classpath.
 *
 * <p>Los valores se escriben sin comillas: un texto con comas rompería las
 * columnas del fichero resultante.
 *
 * @param <T> tipo de la entidad
 */
@Component
public class CsvItemWriter<T> implements ItemWriter<T> {

    /** Ruta del CSV de salida (propiedad {@code csv.output.file.path}). */
    @Value("${csv.output.file.path}")
    private String outputPath;
    /** Serializador CSV de Jackson; deduce las columnas de la clase. */
    private final CsvMapper csvMapper;

    /** Crea el escritor con un {@code CsvMapper} por defecto. */
    public CsvItemWriter() {
        this.csvMapper = new CsvMapper();
    }

    /**
     * Añade los elementos del chunk al fichero.
     *
     * @param chunk elementos a escribir; si está vacío no se toca el fichero
     * @throws IllegalArgumentException si {@code csv.output.file.path} está vacía
     * @throws IOException              si no se puede escribir en el fichero
     */
    @Override
    public void write(Chunk<? extends T> chunk) throws Exception {
        List<? extends T> items = chunk.getItems();

        if (items.isEmpty()) {
            return; // No hay elementos para escribir
        }
        // Validar la ruta de salida
        if (outputPath == null || outputPath.isEmpty()) {
            throw new IllegalArgumentException("El path de salida CSV no está configurado.");
        }
        // Determinar el esquema dinámicamente desde la clase del primer elemento
        Class<?> itemClass = items.get(0).getClass();
        CsvSchema schema = csvMapper.schemaFor(itemClass).withHeader();// añadir header

        // Invertir el orden de los campos.
        //
        // OJO: este bloque NO surte efecto. Las columnas salen en el orden en
        // que la entidad declara sus campos ("id,data";
        // "personaId,nombreCompleto,empleo"), no invertidas. Lo fija
        // JobCsvACsvTest, que se escribió esperando el orden invertido. Por qué
        // Jackson ignora el esquema invertido está sin averiguar; mientras
        // tanto, si una entidad necesita otro orden, lo fiable es anotarla con
        // @JsonPropertyOrder.
        // Convertir el esquema a una lista de columnas, luego invertir esa lista
        List<String> columns = new ArrayList<>();
        schema.getColumnNames().forEach(columns::add);  // Convertir Iterable a List
        Collections.reverse(columns);

        // Crear un nuevo esquema con el orden invertido de las columnas
        CsvSchema.Builder schemaBuilder = CsvSchema.builder();
        for (String column : columns) {
            schemaBuilder.addColumn(column);
        }

        CsvSchema reversedSchema = schemaBuilder.setUseHeader(true).build().withoutQuoteChar(); // eliminar comillas y añadir header

        // Crear archivo y escribir los datos
        File file = new File(outputPath);
        try (FileWriter fileWriter = new FileWriter(file, true)) {
            // Si es la primera vez que escribimos, escribimos los encabezados.
            // (Al llegar aquí FileWriter ya ha creado el fichero, así que lo que
            // decide de verdad es que esté vacío.)
            if (!file.exists() || file.length() == 0) {
                csvMapper.writerFor(itemClass)
                        .with(reversedSchema)
                        .writeValues(fileWriter)
                        .writeAll(items);
            } else {
                CsvSchema schemaWithoutHeader = reversedSchema.withoutHeader(); //eliminar header
                csvMapper.writerFor(itemClass)
                        .with(schemaWithoutHeader)
                        .writeValues(fileWriter)
                        .writeAll(items);
            }
        } catch (IOException e) {
            throw new IOException("Error escribiendo datos en el archivo CSV", e);
        }
    }
}
