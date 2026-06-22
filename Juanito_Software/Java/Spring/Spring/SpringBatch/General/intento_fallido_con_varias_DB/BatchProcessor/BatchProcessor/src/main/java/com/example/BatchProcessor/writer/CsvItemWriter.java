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

@StepScope
public class CsvItemWriter<T> implements ItemWriter<T> {

    @Value("${csv.output.file.path}")
    private String outputPath;
    private final CsvMapper csvMapper;


    public CsvItemWriter() {
        this.csvMapper = new CsvMapper();
    }

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

        //ivertir orden de los campos:
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
            // Si es la primera vez que escribimos, escribimos los encabezados
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
