package com.example.soccer.dto;


import java.time.LocalDate;

public class JugadorDTO {

    private Long id;
    private String nombre;
    private String apellido;
    private LocalDate fechaNac;
    private String posicion;

    // Constructor sin parámetros
    public JugadorDTO() {}

    // Constructor con parámetros
    public JugadorDTO(Long id, String nombre, String apellido, LocalDate fechaNac, String posicion) {
        this.id = id;
        this.nombre = nombre;
        this.apellido = apellido;
        this.fechaNac = fechaNac;
        this.posicion = posicion;
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

    public String getApellido() {
        return apellido;
    }

    public void setApellido(String apellido) {
        this.apellido = apellido;
    }

    public LocalDate getFechaNac() {
        return fechaNac;
    }

    public void setFechaNac(LocalDate fechaNac) {
        this.fechaNac = fechaNac;
    }

    public String getPosicion() {
        return posicion;
    }

    public void setPosicion(String posicion) {
        this.posicion = posicion;
    }
}
