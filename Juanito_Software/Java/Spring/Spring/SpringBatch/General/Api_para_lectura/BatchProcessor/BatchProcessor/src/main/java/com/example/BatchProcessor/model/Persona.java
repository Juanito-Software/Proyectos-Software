package com.example.BatchProcessor.model;

import jakarta.persistence.*;

import java.util.Objects;


/**
 * Entidad JPA que representa una persona en la base de datos.
 * Esta clase almacena información sobre una persona y está asociada a un empleo mediante una relación ManyToOne.
 */
@Entity
@Table(name = "persona")  // Prefijo 'tbl_' añadido al nombre de la tabla
public class Persona {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "personaId")  // Mapea el atributo "personaId" con la columna "persona_id"
    private Long personaId;

    @Column(name = "nombreCompleto", unique = true)  // Restricción de unicidad
    private String nombreCompleto;


    @Column(name = "empleo")  // Restricción de unicidad
    private String empleo;

    public Persona() {}

    public Persona(String nombreCompleto, String empleo) {
        this.nombreCompleto = nombreCompleto;
        this.empleo = empleo;
    }

    // Getters y Setters
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Persona persona = (Persona) o;
        return Objects.equals(nombreCompleto, persona.nombreCompleto);
    }

    @Override
    public int hashCode() {
        return Objects.hash(nombreCompleto); // Basado en el campo "nombre"
    }

}
