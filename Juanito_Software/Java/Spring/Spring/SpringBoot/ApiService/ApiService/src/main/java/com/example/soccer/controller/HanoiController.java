package com.example.soccer.controller;

import com.example.soccer.dto.TowerDTO;
import com.example.soccer.service.HanoiService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api") // Define la ruta base para todos los endpoints en este controlador
public class HanoiController {
    private final HanoiService hanoiService; // Servicio que maneja la lógica de Hanoi

    // Constructor que inyecta el servicio de Hanoi
    public HanoiController(HanoiService hanoiService) {
        this.hanoiService = hanoiService;
    }

    // Endpoint para mover discos
    @PostMapping("/moverDisco")
    public ResponseEntity<TowerDTO> moverDisco(@RequestParam int origen, @RequestParam int destino) {
        try {
            TowerDTO torres = hanoiService.moverDisco(origen, destino);
            if (torres != null) {
                return ResponseEntity.ok(torres); // Devuelve el estado actual de las torres
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }

    // Endpoint para añadir número de discos inicial
    @PostMapping("/añadirDisco")
    public ResponseEntity<String> addDriveTower(@RequestParam Integer numDrives) {
        try {
            hanoiService.addDriveTower(numDrives);
            return ResponseEntity.ok("Discos introducidos.");
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error al añadir discos: " + e.getMessage());
        }
    }


    // Endpoint para mover discos
    @PostMapping("/moverDiscoAuto")
    public ResponseEntity<TowerDTO> moverDiscoAuto(@RequestParam Integer numDrives) {
        try {
            TowerDTO torres = hanoiService.resolver(numDrives);
            if (torres != null) {
                return ResponseEntity.ok(torres); // Devuelve el estado actual de las torres
            } else {
                return ResponseEntity.notFound().build();
            }
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
}
