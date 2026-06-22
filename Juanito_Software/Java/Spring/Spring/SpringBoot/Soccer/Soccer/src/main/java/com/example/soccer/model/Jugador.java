package com.example.soccer.model;

import jakarta.persistence.*;
import java.time.LocalDate;

//Clase que define la Entidad Jugador
@Entity(name="jugador")
public class Jugador {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name="nombre", length=255, nullable=true)
    private String nombre;
    @Column(name="apellido", length=255, nullable=true)
    private String apellido;
    @Column(name="fecha_nac", nullable=true)
    private LocalDate fechaNac;
    @Column(name="posicion", length=255, nullable=true)
    private String posicion;

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
