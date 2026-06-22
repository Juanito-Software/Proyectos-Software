package com.example.BatchProcessor.reader;

import org.springframework.batch.core.StepExecution;
import org.springframework.batch.core.listener.StepExecutionListenerSupport;
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
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.util.*;
import java.util.stream.Collectors;

@Component
public class CsvItemReader<T> extends StepExecutionListenerSupport implements ItemReader<T>, ItemStream {
    // no podemos tomar entityClass antes de ejecutar el job porque no tenemos a la anotacion @StepScope, en vez de eso usamos el beforeStep y extendemos StepExecutionListenerSupport para poder obtenerlo al inicio
    private FlatFileItemReader<T> delegate;

    @Value("${csv.file.path}")
    private String filePath;

    //@Value("#{jobParameters['entityClass']}")
    private String entityClassName;

    private Class<T> entityType;

    // Metodo que se ejecuta antes de iniciar el paso
    @Override
    public void beforeStep(StepExecution stepExecution) {
        // Obtener los parámetros del job y establecer la clase de la entidad
        this.entityClassName = stepExecution.getJobParameters().getString("entityClass");

        // Asegurarse de que entityClassName no sea null
        if (this.entityClassName == null) {
            throw new IllegalArgumentException("The job parameter 'entityClass' is required.");
        }

        // Convertir el nombre de la clase a Class<T>
        try {
            this.entityType = (Class<T>) Class.forName(entityClassName);
        } catch (ClassNotFoundException e) {
            throw new IllegalArgumentException("Class not found: " + entityClassName, e);
        }

        // Llamar a initializeReader() después de que entityType esté configurado
        try {
            initializeReader();
        } catch (IOException | ClassNotFoundException e) {
            throw new RuntimeException("Error initializing the reader", e);
        }
    }


    public void initializeReader() throws IOException, ClassNotFoundException {
        // Crear y configurar el FlatFileItemReader
        this.delegate = new FlatFileItemReader<>();

        // Validar encabezados
        List<String> headers = extractHeaders(filePath);
        validateHeadersAgainstEntity(headers);

        // Configurar el lector
        delegate.setResource(new ClassPathResource(filePath));
        delegate.setLinesToSkip(1);
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
        return delegate.read();
    }

    private List<String> extractHeaders(String filePath) throws IOException {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(new ClassPathResource(filePath).getInputStream()))) {
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
