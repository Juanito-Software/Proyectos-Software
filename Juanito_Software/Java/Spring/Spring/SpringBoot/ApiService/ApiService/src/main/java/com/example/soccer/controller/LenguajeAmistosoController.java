package com.example.soccer.controller;

import com.example.soccer.service.LenguajeAmistosoService;
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

public class LenguajeAmistosoController {
    private final LenguajeAmistosoService lenguajeService;// Servicio que maneja la lógica de formatear segundos

    // Constructor que inyecta el servicio de formatear segundos
    public LenguajeAmistosoController(LenguajeAmistosoService lenguajeService) {
        this.lenguajeService = lenguajeService;
    }

    // Endpoint para formatear una cantidad de tiempo expresada en segundos
    @PostMapping("/segFormat")
    public ResponseEntity<String> format(@RequestParam int seconds) {
        if (seconds < 0) {
            // Validación: los segundos no pueden ser negativos
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body("El número de segundos no puede ser negativo.");
        }
        return ResponseEntity.ok(lenguajeService.formatDuration(seconds));
    }
}
