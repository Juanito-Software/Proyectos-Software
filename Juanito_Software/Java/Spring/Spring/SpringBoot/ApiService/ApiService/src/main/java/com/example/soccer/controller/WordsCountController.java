package com.example.soccer.controller;


import com.example.soccer.service.WordsCountService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador

public class WordsCountController {
    private final WordsCountService wordsCountService;// Servicio que maneja la lógica de contar palabras en una frase

    // Constructor que inyecta el servicio de contar palabras en una frase
    public WordsCountController(WordsCountService wordsCountService) {
        this.wordsCountService = wordsCountService;
    }

    @PostMapping("/countWords")
    public ResponseEntity<String> countWords(@RequestBody String phrase) {
        if (phrase == null || phrase.trim().isEmpty()) {
            // Validación: la frase no puede ser nula o vacía
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("La frase no puede ser nula o vacía.");
        }

        return ResponseEntity.ok(wordsCountService.countWords(phrase));
    }
}
