package com.radiostack.persistence.entity;

import com.radiostack.core.domain.DiaSemana;
import com.radiostack.core.domain.EstadoEmision;
import jakarta.persistence.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "emision")
public class EmisionEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "programa_id")
    private ProgramaEntity programa;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, name = "dia_semana")
    private DiaSemana diaSemana;

    @Column(nullable = false, name = "hora_inicio")
    private LocalDateTime horaInicio;

    @Column(nullable = false, name = "hora_fin")
    private LocalDateTime horaFin;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EstadoEmision estado;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public ProgramaEntity getPrograma() {
        return programa;
    }

    public void setPrograma(ProgramaEntity programa) {
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
}

