package com.radiostack.core.domain;

import java.util.HashSet;
import java.util.Objects;
import java.util.Set;

public class Programa {

    private Long id;
    private String nombre;
    private String descripcion;
    private String categoria;
    private boolean activo;
    private Set<Locutor> locutores = new HashSet<>();

    public Programa() {
    }

    public Programa(Long id, String nombre, String descripcion, String categoria, boolean activo) {
        this.id = id;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.categoria = categoria;
        this.activo = activo;
    }

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

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public String getCategoria() {
        return categoria;
    }

    public void setCategoria(String categoria) {
        this.categoria = categoria;
    }

    public boolean isActivo() {
        return activo;
    }

    public void setActivo(boolean activo) {
        this.activo = activo;
    }

    public Set<Locutor> getLocutores() {
        return locutores;
    }

    public void setLocutores(Set<Locutor> locutores) {
        this.locutores = locutores;
    }

    public void addLocutor(Locutor locutor) {
        this.locutores.add(locutor);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Programa programa = (Programa) o;
        return Objects.equals(id, programa.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

