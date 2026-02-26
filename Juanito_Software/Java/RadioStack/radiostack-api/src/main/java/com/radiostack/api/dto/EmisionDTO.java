package com.radiostack.api.dto;

import java.time.LocalDateTime;

public class EmisionDTO {
    private Long id;
    private Long programaId;
    private String programaNombre;
    private String diaSemana;
    private LocalDateTime horaInicio;
    private LocalDateTime horaFin;
    private String estado;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getProgramaId() { return programaId; }
    public void setProgramaId(Long programaId) { this.programaId = programaId; }
    public String getProgramaNombre() { return programaNombre; }
    public void setProgramaNombre(String programaNombre) { this.programaNombre = programaNombre; }
    public String getDiaSemana() { return diaSemana; }
    public void setDiaSemana(String diaSemana) { this.diaSemana = diaSemana; }
    public LocalDateTime getHoraInicio() { return horaInicio; }
    public void setHoraInicio(LocalDateTime horaInicio) { this.horaInicio = horaInicio; }
    public LocalDateTime getHoraFin() { return horaFin; }
    public void setHoraFin(LocalDateTime horaFin) { this.horaFin = horaFin; }
    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }
}
