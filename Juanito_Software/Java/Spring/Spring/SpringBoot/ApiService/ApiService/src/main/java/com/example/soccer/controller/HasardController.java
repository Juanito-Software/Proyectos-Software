package com.example.soccer.controller;

import com.example.soccer.service.HasardService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador
public class HasardController {

    private final HasardService hasardService;// Servicio que maneja la lógica de hasard

    // Constructor que inyecta el servicio de hasard
    public HasardController(HasardService hasardService) {
        this.hasardService = hasardService;
    }

    // Endpoint para verificar si un número es Harshad
    @GetMapping("/isValid/{n}")
    public ResponseEntity<Boolean> isValid(@PathVariable int n) {
        if (n <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(false); // Harshad sólo aplica a números positivos
        }
        return ResponseEntity.ok(hasardService.isValid(n));
    }

    // Endpoint para obtener el siguiente número Harshad
    @GetMapping("/getNext/{n}")
    public ResponseEntity<Integer> getNext(@PathVariable int n) {
        if (n < 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(null); // Los números negativos no son válidos
        }
        return ResponseEntity.ok(hasardService.getNext(n));
    }

    // Endpoint para obtener una serie de números Harshad
    @GetMapping("/getSerie/{cantidad}")
    public ResponseEntity<ArrayList<Integer>> getSerie(@PathVariable int cantidad) {
        if (cantidad <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ArrayList<>()); // La cantidad debe ser mayor que cero
        }
        return ResponseEntity.ok(hasardService.getSerie(cantidad));
    }

    // Sobrecarga del metodo para incluir el valor de inicio
    @GetMapping("/getSerie/{start}/{cantidad}")
    public ResponseEntity<ArrayList<Integer>> getSerie(@PathVariable int start, @PathVariable int cantidad) {
        if (cantidad <= 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ArrayList<>()); // La cantidad debe ser mayor que cero
        } else if (start < 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ArrayList<>()); // El inicio debe ser un número positivo
        }
        return ResponseEntity.ok(hasardService.getSerie(start, cantidad));
    }
}

