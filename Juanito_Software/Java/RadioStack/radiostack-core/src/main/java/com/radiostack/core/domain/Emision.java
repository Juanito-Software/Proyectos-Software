package com.radiostack.core.domain;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class Emision {

    private Long id;
    private Programa programa;
    private DiaSemana diaSemana;
    private LocalDateTime horaInicio;
    private LocalDateTime horaFin;
    private EstadoEmision estado;
    private List<Comentario> comentarios = new ArrayList<>();

    public Emision() {
    }

    public Emision(Long id,
                   Programa programa,
                   DiaSemana diaSemana,
                   LocalDateTime horaInicio,
                   LocalDateTime horaFin,
                   EstadoEmision estado) {
        this.id = id;
        this.programa = programa;
        this.diaSemana = diaSemana;
        this.horaInicio = horaInicio;
        this.horaFin = horaFin;
        this.estado = estado;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Programa getPrograma() {
        return programa;
    }

    public void setPrograma(Programa programa) {
        this.programa = programa;
    }

    public DiaSemana getDiaSemana() {
        return diaSemana;
    }

    public void setDiaSemana(DiaSemana diaSemana) {
        this.diaSemana = diaSemana;
    }

    public LocalDateTime getHoraInicio() {
        return horaInicio;
    }

    public void setHoraInicio(LocalDateTime horaInicio) {
        this.horaInicio = horaInicio;
    }

    public LocalDateTime getHoraFin() {
        return horaFin;
    }

    public void setHoraFin(LocalDateTime horaFin) {
        this.horaFin = horaFin;
    }

    public EstadoEmision getEstado() {
        return estado;
    }

    public void setEstado(EstadoEmision estado) {
        this.estado = estado;
    }

    public List<Comentario> getComentarios() {
        return comentarios;
    }

    public void setComentarios(List<Comentario> comentarios) {
        this.comentarios = comentarios;
    }

    public void addComentario(Comentario comentario) {
        this.comentarios.add(comentario);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Emision emision = (Emision) o;
        return Objects.equals(id, emision.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

