package com.example.soccer.controller;

import com.example.soccer.service.PseudoCifradoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador

public class PseudoCifradoController {

    private final PseudoCifradoService pseudoCifradoService;// Servicio que maneja la lógica de pseudocifrado

    // Constructor que inyecta el servicio de pseudocifrado
    public PseudoCifradoController(PseudoCifradoService pseudoCifradoService) {
        this.pseudoCifradoService = pseudoCifradoService;
    }

    // Endpoint para cifrar una cadena
    @PostMapping("/encrypt")
    public ResponseEntity<String> encrypt(@RequestParam String text, @RequestParam int iterations) {
        if (text == null || text.isEmpty()) {
            // Validación: el texto no puede ser nulo o vacío
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("El texto no puede ser nulo o vacío.");
        }

        if (iterations <= 0) {
            // Validación: el número de iteraciones debe ser mayor que cero
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("El número de iteraciones debe ser mayor que cero.");
        }
        return ResponseEntity.ok(pseudoCifradoService.encrypt(text, iterations));
    }

    // Endpoint para descifrar una cadena
    @PostMapping("/decrypt")
    public ResponseEntity<String> decrypt(@RequestParam String text, @RequestParam int iterations) {
        if (text == null || text.isEmpty()) {
            // Validación: el texto no puede ser nulo o vacío
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("El texto no puede ser nulo o vacío.");
        }

        if (iterations <= 0) {
            // Validación: el número de iteraciones debe ser mayor que cero
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("El número de iteraciones debe ser mayor que cero.");
        }
        return ResponseEntity.ok(pseudoCifradoService.decrypted(text, iterations));
    }
}
