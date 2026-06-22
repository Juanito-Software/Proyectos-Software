package com.example.BatchProcessor.model;

import jakarta.persistence.*;


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
    private Long empleoId;

    public Empleo(String nombreEmpleo) {
        this.nombreEmpleo = nombreEmpleo;
    }

    // getters y setters
    private String nombreEmpleo;

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


}
