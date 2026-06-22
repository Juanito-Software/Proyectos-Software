package com.example.soccer.controller;


import com.example.soccer.service.NumerosAmigablesService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador

public class NumerosAmigablesController {

    private final NumerosAmigablesService numerosAmigablesService;// Servicio que maneja la logica de Numeros Amigables

    // Constructor que inyecta el servicio Numeros Amigables
    public NumerosAmigablesController(NumerosAmigablesService numerosAmigablesService) {
        this.numerosAmigablesService = numerosAmigablesService;
    }

    // Endpoint para comprobar si dos numeros son Amigables
    @GetMapping("/isFriendly")
    public ResponseEntity<Boolean> isFriendly(@RequestParam int a, @RequestParam int b) {
        if (a < 0 || b < 0) {
            // Validación: los segundos no pueden ser negativos
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(null);
        }
        return ResponseEntity.ok(numerosAmigablesService.isFriendly(a,b));
    }
}