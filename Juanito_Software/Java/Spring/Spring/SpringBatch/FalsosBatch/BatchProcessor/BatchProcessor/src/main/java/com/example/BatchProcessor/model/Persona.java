package com.example.BatchProcessor.model;

import jakarta.persistence.*;

@Entity
public class Persona {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long personaId;

    private String nombre;
    private String apellido;

    @ManyToOne
    @JoinColumn(name = "empleo_id")
    private Empleo empleo;

    public Long getPersonaId() {
        return personaId;
    }

    public String getNombre() {
        return nombre;
    }

    public String getApellido() {
        return apellido;
    }

    public Empleo getEmpleo() {
        return empleo;
    }

    public void setPersonaId(Long personaId) {
        this.personaId = personaId;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public void setApellido(String apellido) {
        this.apellido = apellido;
    }

    public void setEmpleo(Empleo empleo) {
        this.empleo = empleo;
    }
}
