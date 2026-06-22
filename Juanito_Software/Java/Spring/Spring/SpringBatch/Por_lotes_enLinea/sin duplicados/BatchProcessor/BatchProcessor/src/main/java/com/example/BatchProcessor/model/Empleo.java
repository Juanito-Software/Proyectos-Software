package com.example.BatchProcessor.model;

import jakarta.persistence.*;

import java.util.Objects;


/**
 * Entidad JPA que representa un empleo en la base de datos.
 * Esta clase almacena información sobre los empleos disponibles y es utilizada por la clase Persona
 * para asociar un empleo a una persona.
 */
@Entity
@Table(name = "empleo")
public class Empleo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "empleo_id")  // Mapea el atributo "empleoId" con la columna "empleo_id"
    private Long empleoId;

    @Column(name = "nombre_empleo", unique = true)  // Asegura unicidad para el nombre del empleo
    private String nombreEmpleo;

    public Empleo() {

    }

    public Empleo(String nombreEmpleo) {
        this.nombreEmpleo = nombreEmpleo;
    }

    // getters y setters
    public Long getEmpleoId() {
        return empleoId;
    }

    public String getNombreEmpleo() {
        return nombreEmpleo;
    }

    public void setEmpleoId(Long empleoId) {
        this.empleoId = empleoId;
    }

    public void setNombreEmpleo(String nombreEmpleo) {
        this.nombreEmpleo = nombreEmpleo;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Empleo empleo = (Empleo) o;
        return Objects.equals(nombreEmpleo, empleo.nombreEmpleo);
    }

    @Override
    public int hashCode() {
        return Objects.hash(nombreEmpleo); // Basado en el campo "nombre"
    }

}
