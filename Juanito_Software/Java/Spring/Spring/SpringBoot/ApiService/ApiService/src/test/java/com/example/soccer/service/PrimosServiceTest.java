package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

class PrimosServiceTest {

    private final PrimosService primosService = new PrimosService();

    @Test
    void encontrarPrimosConSumandos() {
        // Caso con un número que tiene un primo con sumandos
        ArrayList<Integer> resultado1 = primosService.encontrarPrimosConSumandos(10);
        assertEquals(1, resultado1.size(), "Debería haber 3 primos.");
        assertEquals(5, resultado1.get(0), "El primo con la cadena más larga debería ser 5.");

        // Caso con un número que tiene varios primos con la misma longitud de sumandos
        ArrayList<Integer> resultado2 = primosService.encontrarPrimosConSumandos(20);
        assertEquals(1, resultado2.size(), "Debería haber 2 primos.");
        assertTrue(resultado2.contains(17),"El primos debería ser 17.");

        // Caso con n = 10, primos son [2, 3, 5, 7]
        // El primo 5 puede ser expresado como 2 + 3 (2 sumandos)
        // El primo 7 puede ser expresado como 3 + 4 (2 sumandos)
        // Se espera que 5 y 7 sean devueltos ya que tienen la misma longitud máxima de sumandos.
        ArrayList<Integer> resultado3 = primosService.encontrarPrimosConSumandos(10);
        assertEquals(1, resultado1.size(), "Debería devolver 1 primo.");
        assertTrue(resultado1.contains(5), "Debería incluir el primo 5.");

        // Caso con n = 20, primos son [2, 3, 5, 7, 11, 13, 17, 19]
        // El primo 17 puede ser expresado como 2 + 3 + 4 + 5 + 6 + 7 (6 sumandos)
        // Se espera que 17 sea devuelto ya que tiene la longitud máxima de sumandos.
        ArrayList<Integer> resultado4 = primosService.encontrarPrimosConSumandos(20);
        assertEquals(1, resultado2.size(), "Debería devolver 1 primo.");
        assertEquals(17, resultado2.get(0), "Debería incluir el primo 17.");

        // Caso con n = 30, primos son [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        // El primo 29 puede ser expresado como 15 + 14 (2 sumandos)
        // Se espera que 29 sea devuelto ya que tiene la longitud máxima de sumandos.
        ArrayList<Integer> resultado5 = primosService.encontrarPrimosConSumandos(30);
        assertEquals(1, resultado3.size(), "Debería devolver 1 primo.");
        assertEquals(5, resultado3.get(0), "Debería incluir el primo 5.");
    }
}
