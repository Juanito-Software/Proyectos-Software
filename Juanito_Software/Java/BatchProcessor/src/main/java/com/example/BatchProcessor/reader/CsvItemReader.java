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

/**
 * Lee un CSV del classpath y convierte cada fila en una instancia de la
 * entidad configurada.
 *
 * <p>Por dentro delega en un {@code FlatFileItemReader} de Spring Batch. Lo que
 * añade esta clase es que la entidad no se conoce al compilar: se resuelve al
 * empezar el paso, a partir del parámetro {@code entityClass} del job, y
 * entonces se construye el lector delegado.
 *
 * <p><b>Formato esperado.</b> Primera línea con cabeceras separadas por comas,
 * cada una igual al nombre de un campo de la entidad ({@code id,data} para
 * {@code GenericEntity}). Las filas se asignan a los campos por esas cabeceras
 * usando los setters. No admite comillas con comas dentro ni otro separador.
 *
 * <p><b>Validación.</b> Antes de leer se comprueba que todas las cabeceras
 * existen en la entidad; si alguna no existe, el paso falla sin leer ninguna
 * fila. Solo se miran los campos declarados en la propia clase
 * ({@code getDeclaredFields()}), no los heredados.
 *
 * <p>Implementa {@code ItemStream} para que Spring Batch abra y cierre el
 * fichero en los momentos correctos del paso; los tres métodos solo reenvían
 * la llamada al lector delegado.
 *
 * @param <T> tipo de la entidad, conocido solo en ejecución
 */
@Component
public class CsvItemReader<T> extends StepExecutionListenerSupport implements ItemReader<T>, ItemStream {
    // no podemos tomar entityClass antes de ejecutar el job porque no tenemos a la anotacion @StepScope, en vez de eso usamos el beforeStep y extendemos StepExecutionListenerSupport para poder obtenerlo al inicio

    /** Lector real de Spring Batch; se crea en cada {@link #beforeStep}. */
    private FlatFileItemReader<T> delegate;

    /** Ruta del CSV dentro del classpath (propiedad {@code csv.file.path}). */
    @Value("${csv.file.path}")
    private String filePath;

    //@Value("#{jobParameters['entityClass']}")
    /** Nombre completo de la entidad, copiado del parámetro {@code entityClass}. */
    private String entityClassName;

    /** Clase de la entidad, resuelta por reflexión. */
    private Class<T> entityType;

    /**
     * Se ejecuta antes de empezar el paso: resuelve la entidad y prepara un
     * lector nuevo. Crearlo de nuevo en cada paso hace que un segundo job en el
     * mismo arranque vuelva a leer el fichero desde el principio.
     *
     * @param stepExecution ejecución del paso, con los parámetros del job
     * @throws IllegalArgumentException si falta {@code entityClass}, la clase no
     *                                  existe o una cabecera no encaja
     * @throws RuntimeException         si el fichero no se puede leer
     */
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


    /**
     * Valida las cabeceras del fichero y configura el lector delegado: salta la
     * línea de cabeceras, parte cada fila por comas y vuelca los valores en una
     * instancia nueva de la entidad.
     *
     * @throws IOException              si el fichero no existe o no se puede leer
     * @throws ClassNotFoundException   se declara por compatibilidad; la clase
     *                                  ya está resuelta al llegar aquí
     * @throws IllegalArgumentException si el fichero no tiene cabeceras o alguna
     *                                  no es un campo de la entidad
     */
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

    /**
     * @return la siguiente fila convertida en entidad, o {@code null} al final
     * @throws Exception si una fila no se puede convertir (p. ej. texto en un
     *                   campo numérico)
     */
    @Override
    public T read() throws Exception {
        return delegate.read();
    }

    /**
     * Lee solo la primera línea del fichero y la parte por comas.
     *
     * @param filePath ruta del CSV en el classpath
     * @return nombres de las columnas, en orden
     * @throws IOException              si el fichero no se puede abrir
     * @throws IllegalArgumentException si el fichero está vacío
     */
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

    /**
     * Comprueba que cada cabecera es el nombre de un campo de la entidad.
     * Distingue mayúsculas de minúsculas y no recorta espacios.
     *
     * @param headers cabeceras del fichero
     * @throws IllegalArgumentException con la primera cabecera desconocida
     */
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

    // ── ItemStream: ciclo de vida del fichero, delegado tal cual ──────────────

    /** Abre el fichero; Spring Batch lo llama al empezar el paso. */
    @Override
    public void open(ExecutionContext executionContext) throws ItemStreamException {
        delegate.open(executionContext);
    }

    /** Guarda la posición de lectura al confirmar cada chunk. */
    @Override
    public void update(ExecutionContext executionContext) throws ItemStreamException {
        delegate.update(executionContext);
    }

    /** Cierra el fichero al terminar el paso. */
    @Override
    public void close() throws ItemStreamException {
        delegate.close();
    }
}
