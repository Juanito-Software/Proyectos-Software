package com.example.soccer.controller;

import com.example.soccer.service.HasardService;
import com.example.soccer.service.NumerosPerfectosService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador

public class NumerosPerfectosController {

    private final NumerosPerfectosService numerosPerfectosService;// Servicio que maneja la lógica de Numeros Perfectos

    // Constructor que inyecta el servicio de Numeros Perfectos
    public NumerosPerfectosController(NumerosPerfectosService numerosPerfectosService) {
        this.numerosPerfectosService = numerosPerfectosService;
    }

    // Endpoint para obtener Numeros Perfectos
    @GetMapping("/Perfectos")
    public ResponseEntity<ArrayList<Integer>> Perfecto(@RequestParam int n, @RequestParam int m) {
        return ResponseEntity.ok(numerosPerfectosService.getPerfects(n, m));
    }
}