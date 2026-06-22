package com.example.BatchProcessor.model;

import jakarta.persistence.*;


/**
 * Entidad JPA que representa una persona en la base de datos.
 * Esta clase almacena información sobre una persona y está asociada a un empleo mediante una relación ManyToOne.
 */
@Entity
@Table(name = "persona")  // Prefijo 'tbl_' añadido al nombre de la tabla
public class Persona {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long personaId;

    private String nombreCompleto;

    @ManyToOne
    @JoinColumn(name = "empleo_id")
    private Empleo empleo;

    public Persona() {}

    public Persona(String nombreCompleto, Empleo empleo) {
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

    public Empleo getEmpleo() {
        return empleo;
    }

    public void setEmpleo(Empleo empleo) {
        this.empleo = empleo;
    }
}
