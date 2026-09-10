package com.example.BatchProcessor.writer;

import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.repository.GenericRepository;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;

import java.util.List;

/**
 * Contenedor de {@link ManualItemWriter}. <b>Ningun bean lo usa.</b>
 *
 * <p>Hasta hace poco {@code BatchConfig} construia el bean
 * {@code databaseItemWriter} a partir de {@code ManualItemWriter}, inyectandole
 * el repositorio. Ya no: ese bean es ahora un {@code JpaItemWriter} de Spring
 * Batch. El motivo esta explicado en {@code BatchConfig}, y en corto es la
 * firma de esta clase — {@code <T extends GenericEntity>} —, que ataba el
 * escritor a las entidades que heredaran de {@code GenericEntity} y dejaba
 * fuera a {@code Persona}.
 *
 * <p>Se conserva porque escribir con un repositorio de Spring Data sigue siendo
 * util si alguna vez hace falta logica propia en el guardado —comprobar
 * duplicados, actualizar en vez de insertar, registrar lo escrito—, cosas que
 * {@code JpaItemWriter} no hace. Para usarla habria que declarar el {@code @Bean}
 * en {@code BatchConfig} y aceptar de nuevo la restriccion de la herencia.
 *
 * <p>Aqui vivian tambien un metodo {@code databaseWriter(...)} anotado con
 * {@code @StepScope} pero sin {@code @Bean} —asi que Spring no lo llamaba
 * nunca— y un {@code resolveGenericRepository(...)} que buscaba el repositorio
 * por un nombre construido como {@code getSimpleName() + "Repository"}. Ese
 * bean no existe con ese nombre, de modo que el metodo habria fallado de
 * haberse llegado a ejecutar. Se han retirado: eran inalcanzables y hacian
 * creer, a quien leyera la clase, que la resolucion del repositorio funcionaba
 * de una forma en la que no funciona.
 */
public class DatabaseItemWriter {

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