package com.example.BatchProcessor.model;


import jakarta.persistence.*;

@Entity
public class Venta {

    @Id
    private Long id;
    private String producto;
    private int cantidad;
    private double precio;

    // Constructor
    public Venta(Long id, String producto, int cantidad, double precio) {
        this.id = id;
        this.producto = producto;
        this.cantidad = cantidad;
        this.precio = precio;
    }

    // Getters y setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getProducto() {
        return producto;
    }

    public void setProducto(String producto) {
        this.producto = producto;
    }

    public int getCantidad() {
        return cantidad;
    }

    public void setCantidad(int cantidad) {
        this.cantidad = cantidad;
    }

    public double getPrecio() {
        return precio;
    }

    public void setPrecio(double precio) {
        this.precio = precio;
    }

    @Override
    public String toString() {
        return "Venta{id=" + id + ", producto='" + producto + "', cantidad=" + cantidad + ", precio=" + precio + '}';
    }
}
