package com.example.BatchProcessor.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Empleo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long empleoId;

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
