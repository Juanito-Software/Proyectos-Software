package com.radiostack.core.domain;

import java.time.LocalDateTime;
import java.util.Objects;

public class ChatMessage {

    private Long id;
    private Emision emision;
    private String alias;
    private String contenido;
    private LocalDateTime timestamp;

    public ChatMessage() {
    }

    public ChatMessage(Long id, Emision emision, String alias, String contenido, LocalDateTime timestamp) {
        this.id = id;
        this.emision = emision;
        this.alias = alias;
        this.contenido = contenido;
        this.timestamp = timestamp;
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

    public String getAlias() {
        return alias;
    }

    public void setAlias(String alias) {
        this.alias = alias;
    }

    public String getContenido() {
        return contenido;
    }

    public void setContenido(String contenido) {
        this.contenido = contenido;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ChatMessage that = (ChatMessage) o;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id);
    }
}

