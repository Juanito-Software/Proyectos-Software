package com.example.BatchProcessor.reader;

import org.springframework.batch.item.ExecutionContext;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.ItemStream;
import org.springframework.batch.item.ItemStreamException;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.batch.item.file.mapping.BeanWrapperFieldSetMapper;
import org.springframework.batch.item.file.mapping.DefaultLineMapper;
import org.springframework.batch.item.file.transform.DelimitedLineTokenizer;
import org.springframework.core.io.ClassPathResource;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Component
public class CsvItemReader<T> implements ItemReader<T>, ItemStream {

    private final FlatFileItemReader<T> delegate;
    private final Class<T> entityType;

    @Value("${csv.file.path}")
    private String filePath;

    public CsvItemReader(Class<T> entityType, FlatFileItemReader<T> delegate) {
        this.delegate = delegate;
        this.entityType = entityType;
    }

    @PostConstruct
    public void initializeReader() throws IOException {
        List<String> headers = extractHeaders(filePath);
        validateHeadersAgainstEntity(headers);

        delegate.setResource(new ClassPathResource(filePath));
        // Configurar para saltar la primera línea (encabezados)
        delegate.setLinesToSkip(1); // Saltar la primera línea (encabezado)
        delegate.setLineMapper(new DefaultLineMapper<>() {{
            setLineTokenizer(new DelimitedLineTokenizer() {{
                setNames(headers.toArray(new String[0]));
            }});
            setFieldSetMapper(new BeanWrapperFieldSetMapper<>() {{
                setTargetType(entityType);
            }});
        }});

    }

    @Override
    public T read() throws Exception {
        if (delegate != null) {
            return delegate.read();  // Leer una línea del archivo
        }
        return null;
    }

    private List<String> extractHeaders(String filePath) throws IOException {
        Resource resource = new ClassPathResource(filePath);
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(resource.getInputStream()))) {
            String headerLine = reader.readLine();
            if (headerLine != null) {
                return Arrays.asList(headerLine.split(","));
            } else {
                throw new IllegalArgumentException("The CSV file does not contain headers.");
            }
        }
    }

    private void validateHeadersAgainstEntity(List<String> headers) {
        Set<String> fieldNames = Arrays.stream(entityType.getDeclaredFields())
                .map(Field::getName)
                .collect(Collectors.toSet());

        for (String header : headers) {
            if (!fieldNames.contains(header)) {
                throw new IllegalArgumentException("Unknown header in CSV file: " + header);
            }
        }
    }
    // Delegar métodos de ItemStream al delegado
    @Override
    public void open(ExecutionContext executionContext) throws ItemStreamException {
        delegate.open(executionContext);
    }

    @Override
    public void update(ExecutionContext executionContext) throws ItemStreamException {
        delegate.update(executionContext);
    }

    @Override
    public void close() throws ItemStreamException {
        delegate.close();
    }
}





    /*private final Iterator<T> iterator;

    public CsvItemReader(String filePath, Class<T> clazz) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filePath));

        // Usamos CsvMapper de Jackson para leer el CSV
        CsvMapper csvMapper = new CsvMapper();
        CsvSchema schema = csvMapper.schemaFor(clazz).withHeader().withColumnReordering(true);

        // Convertir las líneas del CSV en objetos del tipo T
        List<T> records = (List<T>) csvMapper.readerFor(clazz).with(schema).readValues(reader).readAll();

        this.iterator = records.iterator();
    }

    @Override
    public T read() {
        if (iterator.hasNext()) {
            return iterator.next();  // Leer el siguiente objeto del tipo T
        }
        return null;  // Si no hay más elementos, devolver null
    }
}*/



    /*private final Iterator<String> iterator;

    public CsvItemReader(String filePath) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filePath));
        this.iterator = reader.lines().iterator();
    }

    @Override
    public T read() {
        if (iterator.hasNext()) {
            String line = iterator.next();
            // Aquí parsea el CSV manualmente según tu clase T
            // Por ejemplo, usando String.split(",")
            return (T) parseLine(line);
        }
        return null;
    }

    private T parseLine(String line) {
        // Implementa la lógica para convertir una línea en un objeto T
        return null;
    }
}*/
