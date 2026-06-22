package com.example.soccer.controller;

import com.example.soccer.service.CsvService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController // Anotación que indica que esta clase es un controlador REST
public class CsvController {

    @Value("${csv.jugadores.path}")
    private String rutaJugadores;

    @Value("${csv.equipos.path}")
    private String rutaEquipos;

    @Value("${csv.participaciones.path}")
    private String rutaParticipacion;

    @Autowired
    private CsvService csvService; // Servicio para manejar la lectura de archivos CSV

    // Endpoint para procesar el archivo CSV de jugadores
    @GetMapping("/procesar-jugadores")
    public ResponseEntity<String> procesarCsvJugadores() {return csvService.procesarJugadores(rutaJugadores);}

    // Endpoint para procesar el archivo CSV de equipos
    @GetMapping("/procesar-equipos")
    public ResponseEntity<String> procesarCSVEquipos() {
        return csvService.procesarEquipos(rutaEquipos);
    }

    // Endpoint para procesar el archivo CSV de participaciones
    @GetMapping("/procesar-participaciones")
    public ResponseEntity<String> procesarCSVParticipaciones() {return csvService.procesarParticipaciones(rutaParticipacion);}


}

