package com.example.BatchProcessor.reader;

import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.item.database.JpaPagingItemReader;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.util.Assert;

/**
 * Fabrica del lector JPA. NO es un bean.
 *
 * <p>Llevaba @Component y @StepScope, lo que registraba un bean llamado
 * 'databaseItemReader' —el nombre de la clase en minuscula inicial— que
 * colisionaba con el @Bean del mismo nombre declarado en BatchConfig. Ganaba
 * este, el componente escaneado, y como esta clase NO implementa ItemReader, el
 * controlador reventaba con un ClassCastException al pedir el bean para
 * componer el paso. La ruta de lectura desde base de datos no funcionaba.
 *
 * <p>Sin anotaciones, el unico bean con ese nombre es el de BatchConfig, que si
 * devuelve un JpaPagingItemReader.
 */
public class DatabaseItemReader {

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