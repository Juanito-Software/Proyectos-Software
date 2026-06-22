package com.example.soccer.model;

import jakarta.persistence.*;
import java.time.LocalDate;

//Clase que define la Entidad Equipo
@Entity(name="equipo")
public class Equipo {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name="nombre", length=255, nullable=true)
    private String nombre;
    @Column(name="ciudad", length=255, nullable=true)
    private String ciudad;
    @Column(name="fecha_fundacion", length=255, nullable=true)
    private LocalDate fechaFundacion;

    // Getters y Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getCiudad() {
        return ciudad;
    }

    public void setCiudad(String ciudad) {
        this.ciudad = ciudad;
    }

    public LocalDate getFechaFundacion() {
        return fechaFundacion;
    }

    public void setFechaFundacion(LocalDate fechaFundacion) {
        this.fechaFundacion = fechaFundacion;
    }
}

