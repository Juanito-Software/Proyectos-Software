package com.example.BatchProcessor.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;

/**
 * Entidad JPA de ejemplo: una persona con su nombre completo y su empleo.
 *
 * <p>Sirve para demostrar que el motor no está atado a {@link GenericEntity}:
 * poniendo {@code entityClass=com.example.BatchProcessor.model.Persona}, las
 * nueve rutas funcionan con esta clase (el CSV de entrada debe tener entonces
 * las cabeceras {@code personaId}, {@code nombreCompleto} y {@code empleo}).
 * También es la forma que devuelve y acepta la API de ejemplo del puerto 8081.
 *
 * <p>El empleo es un texto, no una relación con otra entidad.
 */
@Entity
@Table(name = "persona")
public class Persona {

    /** Clave primaria, autoincremental; columna {@code personaId}. */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "personaId")
    private Long personaId;

    /** Nombre y apellidos; columna {@code nombreCompleto}. */
    @Column(name = "nombreCompleto")
    private String nombreCompleto;

    /** Puesto de trabajo, como texto libre; columna {@code empleo}. */
    @Column(name = "empleo")
    private String empleo;

    /** Constructor vacío: lo necesitan JPA, Jackson y el lector de CSV. */
    public Persona() {}

    /**
     * Crea una persona aún sin id (lo asignará la base al guardarla).
     *
     * @param nombreCompleto nombre y apellidos
     * @param empleo         puesto de trabajo
     */
    public Persona(String nombreCompleto, String empleo) {
        this.nombreCompleto = nombreCompleto;
        this.empleo = empleo;
    }


    public Long getPersonaId() {
        return personaId;
    }

    public void setPersonaId(Long personaId) {
        this.personaId = personaId;
    }

    public String getNombreCompleto() {
        return nombreCompleto;
    }

    public void setNombreCompleto(String nombreCompleto) {
        this.nombreCompleto = nombreCompleto;
    }

    public String getEmpleo() {
        return empleo;
    }

    public void setEmpleo(String empleo) {
        this.empleo = empleo;
    }


}
