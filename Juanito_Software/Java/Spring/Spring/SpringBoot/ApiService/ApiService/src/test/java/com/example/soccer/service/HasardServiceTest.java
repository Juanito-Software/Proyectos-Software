package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

class HasardServiceTest {

    private final HasardService hasardService = new HasardService();

    @Test
    void isValid() {
        // Prueba de números Harshad
        assertTrue(hasardService.isValid(18), "18 debería ser un número Harshad.");
        assertTrue(hasardService.isValid(21), "21 debería ser un número Harshad.");
        assertFalse(hasardService.isValid(22), "22 no debería ser un número Harshad.");
        assertFalse(hasardService.isValid(0), "0 no debería ser un número Harshad.");
        assertTrue(hasardService.isValid(36), "36 debería ser un número Harshad."); // 36 es Harshad porque 3+6=9 y 36 % 9 == 0
    }

    @Test
    void getNext() {
        // Pruebas para el siguiente número Harshad
        assertEquals(20, hasardService.getNext(18), "El siguiente número Harshad después de 18 debería ser 19.");
        assertEquals(21, hasardService.getNext(20), "El siguiente número Harshad después de 20 debería ser 21.");
        assertEquals(24, hasardService.getNext(22), "El siguiente número Harshad después de 22 debería ser 24.");
        assertEquals(1, hasardService.getNext(0), "El siguiente número Harshad después de 0 debería ser 1.");
    }

    @Test
    void getSerie() {
        // Prueba para generar una serie de números Harshad
        ArrayList<Integer> serie = hasardService.getSerie(0, 5);
        assertEquals(5, serie.size(), "Debería haber 5 números en la serie.");
        assertTrue(serie.contains(1), "La serie debería contener 1.");
        assertTrue(serie.contains(2), "La serie debería contener 2.");
        assertTrue(serie.contains(3), "La serie debería contener 3.");
        assertTrue(serie.contains(4), "La serie debería contener 4.");
        assertTrue(serie.contains(5), "La serie debería contener 5.");
    }

    @Test
    void testGetSerie() {
        // Prueba de la sobrecarga de getSerie desde 0
        ArrayList<Integer> serieDesdeCero = hasardService.getSerie(5);
        assertEquals(5, serieDesdeCero.size(), "Debería haber 5 números en la serie comenzando desde 0.");
        assertTrue(serieDesdeCero.contains(1), "La serie debería contener 1.");
        assertTrue(serieDesdeCero.contains(2), "La serie debería contener 2.");
        assertTrue(serieDesdeCero.contains(3), "La serie debería contener 3.");
        assertTrue(serieDesdeCero.contains(4), "La serie debería contener 4.");
        assertTrue(serieDesdeCero.contains(5), "La serie debería contener 5.");
    }
}
