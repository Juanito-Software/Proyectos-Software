package com.example.BatchProcessor.reader;

import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.database.JpaPagingItemReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.Assert;

@Component
@StepScope
public class DatabaseItemReader {
    // podemos tomar entityClass antes de ejecutar el job gracias a la anotacion @StepScope

    public <T> JpaPagingItemReader<T> databaseReader(EntityManagerFactory entityManagerFactory,
                                                     @Value("#{jobParameters['entityClass']}") String entityClassName) throws ClassNotFoundException {
        System.out.println(entityClassName);
        // Convertir el nombre de la clase a una instancia de Class
        Class<T> entityClass = (Class<T>) Class.forName(entityClassName);

        JpaPagingItemReader<T> reader = new JpaPagingItemReader<>();

        // Asegúrate de que la clase de la entidad no sea nula
        Assert.notNull(entityClass, "Entity class cannot be null");

        // Configurar el lector JPA
        reader.setEntityManagerFactory(entityManagerFactory);
        reader.setPageSize(10);  // Define el tamaño de la página
        reader.setSaveState(false);  // Desactivar guardado de estado si no lo necesitas

        // Usamos JPQL en lugar de Criteria
        String jpqlQuery = "SELECT e FROM " + entityClass.getSimpleName() + " e";

        // Establecer el queryString al lector
        reader.setQueryString(jpqlQuery);

        return reader;
    }
}