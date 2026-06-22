package com.example.soccer.service;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class WordsCountServiceTest {

    @Test
    void countWords() {
        WordsCountService wordsCountService = new WordsCountService();

        // Caso 1: Frase simple con palabras repetidas
        String phrase1 = "Hola mundo mundo";
        String expected1 = "{mundo=2, hola=1}"; // Se espera que "hola" aparezca 1 vez y "mundo" 2 veces.
        assertEquals(expected1, wordsCountService.countWords(phrase1), "El conteo de palabras debería ser correcto.");

        // Caso 2: Frase con puntuación
        String phrase2 = "¡Hola! ¿Cómo estás, mundo?";
        String expected2 = "{cómo=1, mundo=1, hola=1, estás=1}"; // Sin repetidos
        assertEquals(expected2, wordsCountService.countWords(phrase2), "El conteo de palabras debería ser correcto con puntuación.");

        // Caso 3: Frase con apóstrofes
        String phrase3 = "El perro de Juan's y el perro de María's son amigos.";
        String expected3 = "{de=2, perro=2, son=1, juan's=1, el=2, y=1, amigos=1, maría's=1}"; // Considera contracciones
        assertEquals(expected3, wordsCountService.countWords(phrase3), "El conteo de palabras debería ser correcto con apóstrofes.");

        // Caso 4: Frase vacía
        String phrase4 = "";
        String expected4 = "{}"; // Un string vacío debería devolver un mapa vacío
        assertEquals(expected4, wordsCountService.countWords(phrase4), "El conteo de palabras debería ser un mapa vacío.");

        // Caso 5: Una sola palabra
        String phrase5 = "Palabra";
        String expected5 = "{palabra=1}"; // Una sola palabra
        assertEquals(expected5, wordsCountService.countWords(phrase5), "El conteo de palabras debería ser correcto para una sola palabra.");
    }
}
