package com.radiostack.core.domain;

import java.time.LocalDateTime;
import java.util.Objects;

public class Comentario {

    private Long id;
    private Emision emision;
    private String autor;
    private String mensaje;
    private LocalDateTime timestamp;
    private EstadoComentario estado;

    public Comentario() {
    }

    public Comentario(Long id,
                      Emision emision,
                      String autor,
                      String mensaje,
                      LocalDateTime timestamp,
                      EstadoComentario estado) {
        this.id = id;
        this.emision = emision;
        this.autor = autor;
        this.mensaje = mensaje;
        this.timestamp = timestamp;
        this.estado = estado;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Emision getEmision() {
        return emision;
    }

    public void setEmision(Emision emision) {
        this.emision = emision;
    }

    public String getAutor() {
        return autor;
    }

    public void setAutor(String autor) {
        this.autor = autor;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public EstadoComentario getEstado() {
        return estado;
    }

    public void setEstado(EstadoComentario estado) {
        this.estado = estado;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Comentario that = (Comentario) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

