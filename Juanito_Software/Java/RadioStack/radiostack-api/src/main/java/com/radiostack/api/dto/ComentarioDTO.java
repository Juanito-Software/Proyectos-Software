package com.radiostack.api.dto;

import java.time.LocalDateTime;

public class ComentarioDTO {
    private Long id;
    private Long emisionId;
    private String autor;
    private String mensaje;
    private LocalDateTime timestamp;
    private String estado;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getEmisionId() { return emisionId; }
    public void setEmisionId(Long emisionId) { this.emisionId = emisionId; }
    public String getAutor() { return autor; }
    public void setAutor(String autor) { this.autor = autor; }
    public String getMensaje() { return mensaje; }
    public void setMensaje(String mensaje) { this.mensaje = mensaje; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
    public String getEstado() { return estado; }
    public void setEstado(String estado) { this.estado = estado; }
}
