package com.example.soccer.controller;


import com.example.soccer.service.CaminandoService;
import com.example.soccer.service.PrimosService;
import jakarta.validation.constraints.Positive;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador
@Validated
public class PrimosController {
    private final PrimosService primosService;// Servicio que maneja la lógica de trabajo con numeros primos

    // Constructor que inyecta el servicio de primos
    public PrimosController(PrimosService primosService) {
        this.primosService = primosService;
    }

    //endpoint para procesar la busqueda de numeros primos
    @PostMapping("/primos")
    public ResponseEntity<ArrayList<Integer>> encontrarPrimosConSumandos(@RequestParam @Positive int n) {
        if (n < 2) {
            // Validación: n debe ser al menos 2 para encontrar primos
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(new ArrayList<>()); // Retorna una lista vacía en caso de error
        }
        return ResponseEntity.ok(primosService.encontrarPrimosConSumandos(n));
    }
}
