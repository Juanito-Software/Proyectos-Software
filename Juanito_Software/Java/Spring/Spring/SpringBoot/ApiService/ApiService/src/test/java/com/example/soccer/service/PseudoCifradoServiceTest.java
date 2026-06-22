package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class PseudoCifradoServiceTest {

    private final PseudoCifradoService pseudoCifradoService = new PseudoCifradoService();

    @Test
    void encrypt() {
        // Caso con cadena normal y 1 encriptación
        String resultado1 = pseudoCifradoService.encrypt("abcdef", 1);
        assertEquals("acebdf", resultado1, "El resultado de la encriptación debería ser 'acebdf'.");

        // Caso con cadena normal y 2 encriptaciones
        String resultado2 = pseudoCifradoService.encrypt("abcdef", 2);
        assertEquals("aedcbf", resultado2, "El resultado de la encriptación debería ser 'abcde'.");

        // Caso con cadena normal y 3 encriptaciones
        String resultado3 = pseudoCifradoService.encrypt("abcdef", 3);
        assertEquals("adbecf", resultado3, "El resultado de la encriptación debería ser 'abcdef'.");

        // Caso con cadena vacía
        String resultado4 = pseudoCifradoService.encrypt("", 1);
        assertEquals("la cadena esta vacia o el numero de Encriptaciones es menor o igual que 0", resultado4,
                "Debería manejar la cadena vacía correctamente.");

        // Caso con número de encriptaciones cero
        String resultado5 = pseudoCifradoService.encrypt("abcdef", 0);
        assertEquals("la cadena esta vacia o el numero de Encriptaciones es menor o igual que 0", resultado5,
                "Debería manejar el número de encriptaciones cero correctamente.");
    }

    @Test
    void decrypted() {
        // Caso con cadena encriptada y 1 desencriptación
        String resultado1 = pseudoCifradoService.decrypted("acebdf", 1);
        assertEquals("abcdef", resultado1, "El resultado de la desencriptación debería ser 'abcdef'.");

        // Caso con cadena encriptada y 2 desencriptaciones
        String resultado2 = pseudoCifradoService.decrypted("acebdf", 2);
        assertEquals("adbecf", resultado2, "El resultado de la desencriptación debería ser 'abcdef'.");

        // Caso con cadena encriptada y 3 desencriptaciones
        String resultado3 = pseudoCifradoService.decrypted("acebdf", 3);
        assertEquals("aedcbf", resultado3, "El resultado de la desencriptación debería ser 'abcdef'.");

        // Caso con cadena vacía
        String resultado4 = pseudoCifradoService.decrypted("", 1);
        assertEquals("la cadena esta vacia o el numero de Encriptaciones es menor o igual que 0", resultado4,
                "Debería manejar la cadena vacía correctamente.");

        // Caso con número de desencriptaciones cero
        String resultado5 = pseudoCifradoService.decrypted("acebdf", 0);
        assertEquals("la cadena esta vacia o el numero de Encriptaciones es menor o igual que 0", resultado5,
                "Debería manejar el número de desencriptaciones cero correctamente.");
    }

    @Test
    void esPar() {
        assertTrue(pseudoCifradoService.esPar(0), "0 debería ser par.");
        assertTrue(pseudoCifradoService.esPar(2), "2 debería ser par.");
        assertTrue(pseudoCifradoService.esPar(4), "4 debería ser par.");
        assertFalse(pseudoCifradoService.esPar(1), "1 no debería ser par.");
        assertFalse(pseudoCifradoService.esPar(3), "3 no debería ser par.");
        assertFalse(pseudoCifradoService.esPar(5), "5 no debería ser par.");
    }
}
