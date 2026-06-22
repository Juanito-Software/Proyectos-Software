package com.example.soccer.dto;

import java.time.LocalDate;

public class ParticipacionDTO {

    private Long id;
    private Long jugadorId;  // ID del jugador
    private Long equipoId;   // ID del equipo
    private LocalDate fechaInicio;
    private LocalDate fechaFin;
    private int dorsal;

    // Constructor sin parámetros
    public ParticipacionDTO() {}

    // Constructor con parámetros
    public ParticipacionDTO(Long id, Long jugadorId, Long equipoId, LocalDate fechaInicio, LocalDate fechaFin, int dorsal) {
        this.id = id;
        this.jugadorId = jugadorId;
        this.equipoId = equipoId;
        this.fechaInicio = fechaInicio;
        this.fechaFin = fechaFin;
        this.dorsal = dorsal;
    }

    // Getters y Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getJugadorId() {
        return jugadorId;
    }

    public void setJugadorId(Long jugadorId) {
        this.jugadorId = jugadorId;
    }

    public Long getEquipoId() {
        return equipoId;
    }

    public void setEquipoId(Long equipoId) {
        this.equipoId = equipoId;
    }

    public LocalDate getFechaInicio() {
        return fechaInicio;
    }

    public void setFechaInicio(LocalDate fechaInicio) {
        this.fechaInicio = fechaInicio;
    }

    public LocalDate getFechaFin() {
        return fechaFin;
    }

    public void setFechaFin(LocalDate fechaFin) {
        this.fechaFin = fechaFin;
    }

    public int getDorsal() {
        return dorsal;
    }

    public void setDorsal(int dorsal) {
        this.dorsal = dorsal;
    }
}
