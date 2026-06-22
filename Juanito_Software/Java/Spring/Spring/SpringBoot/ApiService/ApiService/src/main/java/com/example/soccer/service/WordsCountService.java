package com.example.soccer.service;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class WordsCountService {

        //patern \b(\w+)'?(\w)+\b
        // Metodo para contar las palabras repetidas en una frase


    public String countWords (String phrase){
        phrase = phrase.replace("\\n", "");// remplazar \n

        // Define el patrón utilizando la misma expresión regular
        Pattern pattern = Pattern.compile("[\\p{L}[0-9]]+(?:'[\\p{L}]+)?");
        Matcher matcher = pattern.matcher(phrase);

        //\p{L} asegura que se capturen todas las letras, sin importar el idioma, acentos etz
        //0-9 permite que coincidan números.  + una o mas coincidencias
        //(?: ... ): Esto indica un grupo de no captura
        //': Este carácter literal es un apóstrofe.
        //[\p{L}] Aquí se vuelve a utilizar la clase de caracteres que hemos definido antes, pero solo permitiendo letras después de un apóstrofe.
        //?: Este operador indica que lo que precede (en este caso, el grupo que contiene el apóstrofe seguido de letras) es opcional. Esto significa que la coincidencia puede o no tener un apóstrofe seguido de letras.

        // Mapa para contar las repeticiones de cada palabra
        Map<String, Integer> count = new HashMap<>();

        // Buscar todas las coincidencias
        while (matcher.find()) {
            // Extraer la palabra encontrada
            String word = matcher.group();

            // Normalizar la palabra a minúsculas para el conteo uniforme
            word = word.toLowerCase();

            // Contar la palabra en el mapa
            count.put(word, count.getOrDefault(word, 0) + 1);
        }

        // Retornar el mapa de palabras y sus frecuencias
        return count.toString();
    }


    public String countWords2 (String phrase){
        Map<String, Integer> count = new HashMap<>();

        phrase = phrase.replace("\\n", ":");
        String[] words = phrase.split("[\\s[¡!¿?]\\p{Punct}&&[^']]+|'(?!\\w)|(?<!\\w)'");     // dividir la cadena phrase en palabras, utilizando como delimitadores cualquier combinación de espacios en blanco, caracteres de puntuación, y también gestionando apóstrofes de manera que se conserven las contracciones



        // Recorrer las palabras y contar las repeticiones
        for (String word : words) {
            word = word.trim(); // Eliminar espacios en blanco alrededor
            if (!word.isEmpty()) { // Verificar que no sea vacío
                // Normalizar la palabra (puedes agregar más normalizaciones si lo deseas)
                word = word.toLowerCase(); // Convertir a minúsculas para evitar diferencias por mayúsculas
                count.put(word, count.getOrDefault(word, 0) + 1); // Contar la palabra
            }
        }

        return count.toString(); // Retornar el mapa con las palabras y sus conteos
    }
}