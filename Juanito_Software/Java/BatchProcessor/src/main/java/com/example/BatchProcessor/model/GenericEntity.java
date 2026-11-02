package com.example.BatchProcessor.model;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Entidad de ejemplo y por defecto: un id y un texto libre.
 *
 * <p>Es la que usa la configuración actual ({@code entityClass} en
 * {@code application.properties}) y la que describe {@code input.csv}, cuyas
 * cabeceras deben coincidir con los campos de esta clase ({@code id},
 * {@code data}).
 *
 * <p>Lombok genera getters, setters, {@code equals/hashCode}, {@code toString}
 * y los dos constructores. El constructor vacío es imprescindible: lo usan
 * JPA, Jackson y el lector de CSV para instanciar la clase por reflexión.
 *
 * <p>Ojo con el id: es {@code IDENTITY} (lo genera la base), pero el CSV
 * también trae una columna {@code id}. Al escribir con {@code JpaItemWriter}
 * ({@code merge}), un id que ya exista en la tabla se actualiza en vez de
 * insertarse. Está anotado como pendiente en {@code MAINTENANCE.md}.
 */
@Entity
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "genericentity")
public class GenericEntity {

    /** Clave primaria, autoincremental en la base de datos. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** Contenido del registro: texto libre. */
    @Column
    private String data;
}
