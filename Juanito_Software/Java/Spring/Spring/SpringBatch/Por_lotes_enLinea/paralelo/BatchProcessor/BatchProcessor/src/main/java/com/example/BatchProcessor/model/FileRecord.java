package com.example.BatchProcessor.model;


/**
 * Clase de modelo que representa un registro de archivo CSV.
 * Esta clase se utiliza para mapear los datos de cada línea de un archivo CSV a un objeto Java.
 */
public class FileRecord {
    private String nombre;
    private String apellido;
    private String nombreEmpleo;

    // Constructor vacío
    public FileRecord() {
    }

    // Constructor completo
    public FileRecord(String nombre, String apellido, String nombreEmpleo) {
        this.nombre = nombre;
        this.apellido = apellido;
        this.nombreEmpleo = nombreEmpleo;
    }

    // Getters y Setters
    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getApellido() {
        return apellido;
    }

    public void setApellido(String apellido) {
        this.apellido = apellido;
    }

    public String getNombreEmpleo() {
        return nombreEmpleo;
    }

    public void setNombreEmpleo(String nombreEmpleo) {
        this.nombreEmpleo = nombreEmpleo;
    }

    // Metodo para obtener el registro completo como un string CSV (por ejemplo)
    public String getRawData() {
        return nombre + "," + apellido + "," + nombreEmpleo; // Devuelve los datos en formato CSV
    }

    // toString para depuración
    @Override
    public String toString() {
        return "FileRecord{" +
                "nombre='" + nombre + '\'' +
                ", apellido='" + apellido + '\'' +
                ", nombreEmpleo='" + nombreEmpleo + '\'' +
                '}';
    }
}
