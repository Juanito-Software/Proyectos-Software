package com.example.soccer.service;

import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class HanoiService2 {

    public List<String> torresHanoi(int discos, int origen, int auxiliar, int destino) {
        List<String> movimientos = new ArrayList<>();

        // Caso base: si solo hay un disco, moverlo directamente al destino.
        if (discos == 1) {
            movimientos.add("Mover disco 1 de Torre " + origen + " a Torre " + destino);
            return movimientos;
        }

        // Paso 1: Mover todos los discos menos el último (discos-1) desde la torre origen a la torre auxiliar.
        movimientos.addAll(torresHanoi(discos - 1, origen, destino, auxiliar));

        // Paso 2: Mover el disco más grande (el último) directamente de la torre origen a la torre destino.
        movimientos.add("Mover disco " + discos + " de Torre " + origen + " a Torre " + destino);

        // Paso 3: Mover los discos-1 discos de la torre auxiliar a la torre destino.
        movimientos.addAll(torresHanoi(discos - 1, auxiliar, origen, destino));

        return movimientos;
    }
}

// 3 discos
//  "Mover disco 1 de la Torre 1 a Torre 3",
//  "Mover disco 2 de la Torre 1 a Torre 2",
//  "Mover disco 1 de la Torre 3 a Torre 2",
//  "Mover disco 3 de la Torre 1 a Torre 3",
//  "Mover disco 1 de la Torre 2 a Torre 1",
//  "Mover disco 2 de la Torre 2 a Torre 3",
//  "Mover disco 1 de la Torre 1 a Torre 3"