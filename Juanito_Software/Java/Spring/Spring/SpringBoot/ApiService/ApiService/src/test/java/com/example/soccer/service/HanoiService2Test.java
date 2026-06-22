package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class HanoiService2Test {

    @Test
    void torresHanoi() {
        HanoiService2 hanoiService2 = new HanoiService2();

        // Caso con 1 disco
        List<String> movimientos1 = hanoiService2.torresHanoi(1, 1, 2, 3);
        assertEquals(1, movimientos1.size(), "Debería haber 1 movimiento.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 3", movimientos1.get(0), "El movimiento debería ser correcto.");

        // Caso con 2 discos
        List<String> movimientos2 = hanoiService2.torresHanoi(2, 1, 2, 3);
        assertEquals(3, movimientos2.size(), "Debería haber 3 movimientos.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 2", movimientos2.get(0), "El primer movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 1 a Torre 3", movimientos2.get(1), "El segundo movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 2 a Torre 3", movimientos2.get(2), "El tercer movimiento debería ser correcto.");

        // Caso con 3 discos
        List<String> movimientos3 = hanoiService2.torresHanoi(3, 1, 2, 3);
        assertEquals(7, movimientos3.size(), "Debería haber 7 movimientos.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 3", movimientos3.get(0), "El primer movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 1 a Torre 2", movimientos3.get(1), "El segundo movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 3 a Torre 2", movimientos3.get(2), "El tercer movimiento debería ser correcto.");
        assertEquals("Mover disco 3 de Torre 1 a Torre 3", movimientos3.get(3), "El cuarto movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 2 a Torre 1", movimientos3.get(4), "El quinto movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 2 a Torre 3", movimientos3.get(5), "El sexto movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 3", movimientos3.get(6), "El séptimo movimiento debería ser correcto.");

        // Caso con 4 discos
        List<String> movimientos4 = hanoiService2.torresHanoi(4, 1, 2, 3);
        assertEquals(15, movimientos4.size(), "Debería haber 15 movimientos.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 2", movimientos4.get(0), "El primer movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 1 a Torre 3", movimientos4.get(1), "El segundo movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 2 a Torre 3", movimientos4.get(2), "El tercer movimiento debería ser correcto.");
        assertEquals("Mover disco 3 de Torre 1 a Torre 2", movimientos4.get(3), "El cuarto movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 3 a Torre 1", movimientos4.get(4), "El quinto movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 3 a Torre 2", movimientos4.get(5), "El sexto movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 2", movimientos4.get(6), "El séptimo movimiento debería ser correcto.");
        assertEquals("Mover disco 4 de Torre 1 a Torre 3", movimientos4.get(7), "El octavo movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 2 a Torre 3", movimientos4.get(8), "El noveno movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 2 a Torre 1", movimientos4.get(9), "El décimo movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 3 a Torre 1", movimientos4.get(10), "El undécimo movimiento debería ser correcto.");
        assertEquals("Mover disco 3 de Torre 2 a Torre 3", movimientos4.get(11), "El duodécimo movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 1 a Torre 2", movimientos4.get(12), "El décimo tercer movimiento debería ser correcto.");
        assertEquals("Mover disco 2 de Torre 1 a Torre 3", movimientos4.get(13), "El décimo cuarto movimiento debería ser correcto.");
        assertEquals("Mover disco 1 de Torre 2 a Torre 3", movimientos4.get(14), "El décimo quinto movimiento debería ser correcto.");
    }
}
