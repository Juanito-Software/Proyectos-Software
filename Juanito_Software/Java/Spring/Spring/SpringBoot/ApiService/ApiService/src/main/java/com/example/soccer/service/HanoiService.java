package com.example.soccer.service;

import com.example.soccer.dto.TowerDTO;

import java.util.Stack;

public class HanoiService {

    private Stack<Integer> tower1;
    private Stack<Integer> tower2;
    private Stack<Integer> tower3 = new Stack<>();

    // Constructor vacío
    public HanoiService() {
        tower1 = new Stack<>();
        tower2 = new Stack<>();
        tower3 = new Stack<>();
    }

    /**
    // O puedes tener un constructor que inicialice el número de discos
    public HanoiService(int numDiscos) {
        this(); // Llama al constructor vacío
        addDriveTower(numDiscos); // Añade discos a la torre inicial
    }*/

    // Método para añadir discos a la torre inicial
    public void addDriveTower(Integer numDrives) {
        for (int i = numDrives; i >= 1; i--) {
            tower1.push(i); // Añadir discos de mayor a menor a tower1
        }
    }

    // Método para mover discos entre torres
    public TowerDTO moverDisco(int origen, int destino) {
        Stack<Integer> towerOrigin = getTowerByIndex(origen);
        Stack<Integer> towerDestiny = getTowerByIndex(destino);

        // Validar que las torres existen
        if (towerOrigin == null || towerDestiny == null) {
            System.out.println("Torre inválida.");
            return null; // O lanzar una excepción
        }

        // Verificar si la torre de origen está vacía
        if (towerOrigin.isEmpty()) {
            System.out.println("No hay discos en la torre de origen.");
            return null; // O lanzar una excepción
        }

        int discoOrigen = towerOrigin.peek(); // Ver el disco en la cima de la torre de origen

        // Regla: No se puede mover un disco más grande sobre uno más pequeño
        if (!towerDestiny.isEmpty() && towerDestiny.peek() < discoOrigen) {
            System.out.println("Movimiento inválido: no puedes poner un disco más grande sobre uno más pequeño.");
            return null; // O lanzar una excepción
        }

        // Si se cumplen las reglas, realizar el movimiento
        towerDestiny.push(towerOrigin.pop());
        System.out.println("Mover disco " + discoOrigen + " de la torre " + origen + " a la torre " + destino + ".");

        // Devolver el estado actual de las torres
        return new TowerDTO((Stack<Integer>) tower1.clone(), (Stack<Integer>) tower2.clone(), (Stack<Integer>) tower3.clone());
    }

    // Método para obtener la torre según el índice
    private Stack<Integer> getTowerByIndex(int index) {
        switch (index) {
            case 1: return tower1;
            case 2: return tower2;
            case 3: return tower3;
            default: return null;
        }
    }

    public TowerDTO  resolver(Integer numDrives){
        if (numDrives==1) {
            moverDisco(1,3);
        }else if (numDrives==2){
            moverDisco(1,2);
            moverDisco(1,3);
            moverDisco(2,3);
        }else if (numDrives==3) {
            moverDisco(1,3);
            moverDisco(1,2);
            moverDisco(3,2);
            moverDisco(1,3);
            moverDisco(2,1);
            moverDisco(2,3);
            moverDisco(1,3);
        }else if(numDrives==4){
            moverDisco(1,2);
            moverDisco(1,3);
            moverDisco(2,3);
            moverDisco(1,2);
            moverDisco(3,1);
            moverDisco(3,2);
            moverDisco(1,2);
            moverDisco(1,3);
            moverDisco(2,1);
            moverDisco(2,3);
            moverDisco(1,2);
            moverDisco(3,1);
            moverDisco(2,1);
            moverDisco(2,3);
            moverDisco(1,2);
            moverDisco(1,3);
            moverDisco(2,3);

        }
        return new TowerDTO((Stack<Integer>) tower1.clone(), (Stack<Integer>) tower2.clone(), (Stack<Integer>) tower3.clone());
    }
}
