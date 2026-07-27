package com.example.soccer.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.example.soccer.service.HanoiService2;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api") // Define la ruta base para todos los endpoints en este controlador
public class HanoiController2 {

    private static final Logger log = LoggerFactory.getLogger(HanoiController2.class);
    private final HanoiService2 hanoiService; // Servicio que maneja la lógica de Hanoi

    // Constructor que inyecta el servicio de Hanoi
    public HanoiController2(HanoiService2 hanoiService2) {
        this.hanoiService = hanoiService2;
    }


    // Endpoint para añadir número de discos inicial
    @PostMapping("/torresHanoi")
    public ResponseEntity<List<String>> torresHanoi(@RequestParam int numDrives) {
        try {
            return ResponseEntity.ok(hanoiService.torresHanoi(numDrives,1,2,3));
        } catch (Exception e) {
            log.error("Error al resolver las torres de Hanoi", e);
            return ResponseEntity.notFound().build();
        }
    }
}