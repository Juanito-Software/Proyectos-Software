package com.radiostack.api.dto;

import java.time.LocalDateTime;

public class ChatMessageDTO {
    private Long id;
    private Long emisionId;
    private String alias;
    private String contenido;
    private LocalDateTime timestamp;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getEmisionId() { return emisionId; }
    public void setEmisionId(Long emisionId) { this.emisionId = emisionId; }
    public String getAlias() { return alias; }
    public void setAlias(String alias) { this.alias = alias; }
    public String getContenido() { return contenido; }
    public void setContenido(String contenido) { this.contenido = contenido; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}
