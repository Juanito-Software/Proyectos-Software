package com.radiostack.api.dto;

import java.util.Set;

public class ProgramaDTO {
    private Long id;
    private String nombre;
    private String descripcion;
    private String categoria;
    private boolean activo;
    private Set<Long> locutorIds;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getDescripcion() { return descripcion; }
    public void setDescripcion(String descripcion) { this.descripcion = descripcion; }
    public String getCategoria() { return categoria; }
    public void setCategoria(String categoria) { this.categoria = categoria; }
    public boolean isActivo() { return activo; }
    public void setActivo(boolean activo) { this.activo = activo; }
    public Set<Long> getLocutorIds() { return locutorIds; }
    public void setLocutorIds(Set<Long> locutorIds) { this.locutorIds = locutorIds; }
}
