package com.example.soccer.controller;

import com.example.soccer.dto.CaminataDTO;
import com.example.soccer.service.CaminandoService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador
public class CaminandoController {

    private final CaminandoService caminandoService;// Servicio que maneja la lógica de paseo

    // Constructor que inyecta el servicio de paseo
    public CaminandoController(CaminandoService caminandoService) {
        this.caminandoService = caminandoService;
    }

    //endpoint para procesar el paseo mediante los minutos y el numero de direcciones
    @PostMapping("/paseo")
    public ResponseEntity<String> procesarPaseo(@RequestBody CaminataDTO caminataDTO) {
        try {
            boolean resultado = caminandoService.CalcularTiempoyCamino(caminataDTO.getMinutos(), caminataDTO.getDirecciones());
            return ResponseEntity.ok(resultado ? "El paseo es válido" : "El paseo no es válido");
        } catch (IllegalArgumentException e) {
            // Captura la excepción lanzada por el servicio y devuelve un mensaje de error
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}
