package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.GenericEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * Repositorio Spring Data para {@link GenericEntity} y sus subclases.
 *
 * <p>El flujo de los jobs <b>ya no lo usa</b>: el escritor a base de datos es un
 * {@code JpaItemWriter} que persiste cualquier {@code @Entity}. Se conserva
 * porque los tests lo usan para preparar y comprobar los datos de la base, y
 * porque lo usa el escritor antiguo que se guarda como referencia en
 * {@code writer.DatabaseItemWriter}.
 *
 * @param <T>  tipo de entidad, {@link GenericEntity} o una subclase
 * @param <ID> tipo de la clave primaria ({@code Long})
 */
@Repository
public interface GenericRepository<T extends GenericEntity, ID> extends JpaRepository<T, ID> {
    // Sin métodos propios: los CRUD de JpaRepository bastan.
}
