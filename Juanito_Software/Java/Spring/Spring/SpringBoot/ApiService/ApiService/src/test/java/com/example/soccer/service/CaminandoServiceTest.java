package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CaminandoServiceTest {

    private final CaminandoService caminandoService = new CaminandoService();

    @Test
    void calcularTiempoyCamino_ValidInput_ReturnsTrue() {
        // Dado
        int minutos = 4;
        String[] direcciones = {"n", "s", "e", "w"};

        // Cuando
        boolean result = caminandoService.CalcularTiempoyCamino(minutos, direcciones);

        // Entonces
        assertTrue(result, "Debería devolver true porque las direcciones vuelven al punto inicial.");
    }

    @Test
    void calcularTiempoyCamino_InsufficientDirections_ReturnsFalse() {
        // Dado
        int minutos = 5;
        String[] direcciones = {"n", "s", "e"};

        // Cuando
        boolean result = caminandoService.CalcularTiempoyCamino(minutos, direcciones);

        // Entonces
        assertFalse(result, "Debería devolver false porque el número de direcciones es menor que los minutos.");
    }

    @Test
    void calcularTiempoyCamino_InvalidMinutes_ThrowsException() {
        // Dado
        int minutos = -1;
        String[] direcciones = {"n", "s"};

        // Cuando y Entonces
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            caminandoService.CalcularTiempoyCamino(minutos, direcciones);
        });

        assertEquals("Los minutos deben ser mayores a cero.", exception.getMessage());
    }

    @Test
    void calcularTiempoyCamino_EmptyDirections_ThrowsException() {
        // Dado
        int minutos = 2;
        String[] direcciones = {};

        // Cuando y Entonces
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            caminandoService.CalcularTiempoyCamino(minutos, direcciones);
        });

        assertEquals("Las direcciones no pueden ser nulas o vacías.", exception.getMessage());
    }

    @Test
    void calcularTiempoyCamino_InvalidDirection_ReturnsFalse() {
        // Dado
        int minutos = 3;
        String[] direcciones = {"n", "x", "s"}; // 'x' es inválido

        // Cuando
        boolean result = caminandoService.CalcularTiempoyCamino(minutos, direcciones);

        // Entonces
        assertFalse(result, "Debería devolver false debido a una dirección inválida.");
    }
}
