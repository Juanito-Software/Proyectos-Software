package com.example.soccer.dto;

import java.time.LocalDate;

public class EquipoDTO {

    private Long id;
    private String nombre;
    private String ciudad;
    private LocalDate fechaFundacion;

    // Constructor
    public EquipoDTO() {}

    public EquipoDTO(Long id, String nombre, String ciudad, LocalDate fechaFundacion) {
        this.id = id;
        this.nombre = nombre;
        this.ciudad = ciudad;
        this.fechaFundacion = fechaFundacion;
    }

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
