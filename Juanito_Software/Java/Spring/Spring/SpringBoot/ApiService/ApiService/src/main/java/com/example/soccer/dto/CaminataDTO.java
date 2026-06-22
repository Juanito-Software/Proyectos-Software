package com.example.soccer.dto;

// Clase que representa un objeto de transferencia de datos (DTO) para una caminata
public class CaminataDTO {
    private Integer minutos;// Duración de la caminata en minutos
    private String[] direcciones;// Array que almacena las direcciones de la caminata

    // Constructor sin parametros
    public CaminataDTO() {}

    public Integer getMinutos() {
        return minutos;
    }

    public void setMinutos(Integer minutos) {
        this.minutos = minutos;
    }

    public String[] getDirecciones() {
        return direcciones;
    }

    public void setDirecciones(String[] direcciones) {
        this.direcciones = direcciones;
    }
}
