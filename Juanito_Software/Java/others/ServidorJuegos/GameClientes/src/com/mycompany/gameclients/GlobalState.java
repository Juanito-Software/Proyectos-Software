/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.gameclients;

import java.util.ArrayList;
import java.util.List;
import javax.swing.ImageIcon;

/**
 *
 * @author User
 */
public class GlobalState {
    private static GlobalState instance;
    private ImageIcon empresaLogo;
    private String empresaSeleccionada;
    private List<Observer> observers;

    // Constructor privado para evitar instanciación directa
    private GlobalState() {
        observers = new ArrayList<>();
    }

    public static GlobalState getInstance() {
        if (instance == null) {
            instance = new GlobalState();
        }
        return instance;
    }

    public void addObserver(Observer observer) {
        observers.add(observer);
    }
    
    private void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(empresaSeleccionada, empresaLogo);
        }
    }
    
    public void setEmpresaSeleccionada(String empresaSeleccionada, ImageIcon empresaLogo) {
        this.empresaSeleccionada = empresaSeleccionada;
        this.empresaLogo = empresaLogo;
        notifyObservers();
    }

    public ImageIcon getEmpresaLogo() {
        return empresaLogo;
    }

    // Método para obtener el nombre de la empresa seleccionada
    public String getEmpresaSeleccionada() {
        return empresaSeleccionada;
    }
}


