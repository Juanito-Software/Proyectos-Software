package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LenguajeAmistosoServiceTest {

    private final LenguajeAmistosoService lenguajeAmistosoService = new LenguajeAmistosoService();

    @Test
    void formatDuration() {
        // Caso de 0 segundos
        assertEquals("ahora", lenguajeAmistosoService.formatDuration(0), "0 segundos debería devolver 'ahora'.");

        // Caso de 1 segundo
        assertEquals("1 segundo", lenguajeAmistosoService.formatDuration(1), "1 segundo debería devolver '1 segundo'.");

        // Caso de 1 minuto
        assertEquals("1 minuto", lenguajeAmistosoService.formatDuration(60), "60 segundos debería devolver '1 minuto'.");

        // Caso de 1 hora
        assertEquals("1 hora", lenguajeAmistosoService.formatDuration(3600), "3600 segundos debería devolver '1 hora'.");

        // Caso de 1 día
        assertEquals("1 día", lenguajeAmistosoService.formatDuration(86400), "86400 segundos debería devolver '1 día'.");

        // Caso de 1 año
        assertEquals("1 año", lenguajeAmistosoService.formatDuration(31536000), "31536000 segundos debería devolver '1 año'.");

        // Caso de múltiples unidades (1 año, 1 día, 1 hora, 1 minuto y 1 segundo)
        assertEquals("1 año, 1 minuto y 1 segundo",
                lenguajeAmistosoService.formatDuration(31536061),
                "31536061 segundos debería devolver '1 año, 1 minuto y 1 segundo'.");

        // Caso de múltiples unidades (2 años, 3 días, 4 horas, 5 minutos y 6 segundos)
        assertEquals("2 años, 55 días, 2 horas, 56 minutos y 6 segundos",
                lenguajeAmistosoService.formatDuration(67834566),
                "67834566 segundos debería devolver '2 años, 55 días, 2 horas, 56 minutos y 6 segundos'.");

        // Caso de múltiples unidades sin el último componente
        assertEquals("3 años, 62 días, 9 horas, 46 minutos y 40 segundos",
                lenguajeAmistosoService.formatDuration(100000000),
                "100000000 segundos debería devolver '3 años, 62 días, 9 horas, 46 minutos y 40 segundos'.");
    }
}
