package com.example.BatchProcessor.writer;

import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.repository.GenericRepository;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;
import org.springframework.util.Assert;

import java.util.List;

@Component
public class DatabaseItemWriter {


    private ApplicationContext applicationContext; // Inyectar el contexto de la aplicación


    public DatabaseItemWriter(ApplicationContext applicationContext) {
        this.applicationContext = applicationContext;
    }

    @StepScope
    public <T extends GenericEntity> ManualItemWriter<T> databaseWriter(
            @Value("#{jobParameters['entityClass']}") Class<T> clazz) {
        // Asegúrate de que la clase de la entidad no sea nula
        Assert.notNull(clazz, "Entity class cannot be null");

        // Resolver el repositorio adecuado basado en el tipo de la clase
        GenericRepository<T, Long> genericRepository = resolveGenericRepository(clazz);

        // Crear y devolver ManualItemWriter
        return new ManualItemWriter<>(genericRepository);
    }

    /**
     * Metodo auxiliar para resolver el repositorio genérico según la clase de la entidad.
     */
    private <T extends GenericEntity> GenericRepository<T, Long> resolveGenericRepository(Class<T> clazz) {
        String beanName = clazz.getSimpleName() + "Repository"; // Se asume que el nombre del repositorio sigue este formato
        return (GenericRepository<T, Long>) applicationContext.getBean(beanName, GenericRepository.class);
    }

    // Implementación personalizada de ItemWriter
    public static class ManualItemWriter<T extends GenericEntity> implements ItemWriter<T> {
        private final GenericRepository<T, Long> genericRepository; // Usar el repositorio genérico

        // Inyectar el repositorio en el constructor
        public ManualItemWriter(GenericRepository<T, Long> genericRepository) {
            this.genericRepository = genericRepository;
        }

        @Override
        public void write(Chunk<? extends T> chunk) throws Exception {
            List<? extends T> items = chunk.getItems();

            if (items.isEmpty()) {
                return; // No hay elementos para escribir
            }

            // Guardar todos los elementos utilizando el repositorio
            try {
                genericRepository.saveAll(items);
            } catch (Exception e) {
                throw new Exception("Error al guardar los elementos en la base de datos", e);
            }
        }
    }
}