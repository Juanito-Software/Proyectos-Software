package com.radiostack.core.domain;

import java.util.Objects;

public class Locutor {

    private Long id;
    private String nombreArtistico;
    private Usuario usuario;

    public Locutor() {
    }

    public Locutor(Long id, String nombreArtistico, Usuario usuario) {
        this.id = id;
        this.nombreArtistico = nombreArtistico;
        this.usuario = usuario;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getNombreArtistico() {
        return nombreArtistico;
    }

    public void setNombreArtistico(String nombreArtistico) {
        this.nombreArtistico = nombreArtistico;
    }

    public Usuario getUsuario() {
        return usuario;
    }

    public void setUsuario(Usuario usuario) {
        this.usuario = usuario;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Locutor locutor = (Locutor) o;
        return Objects.equals(id, locutor.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

