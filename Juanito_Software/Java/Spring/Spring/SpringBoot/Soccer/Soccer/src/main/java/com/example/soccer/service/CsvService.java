package com.example.soccer.service;

import com.opencsv.CSVReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;


// Servicio para la lectura de CSV, utilizado por el CsvController
@Service // Anotación que indica que esta clase es un servicio de Spring
public class CsvService {
    
    @Autowired
    private JugadorService jugadorService; // Servicio para operaciones con jugadores

    @Autowired
    private EquipoService equipoService; // Servicio para operaciones con equipos

    @Autowired
    private ParticipacionService participacionService; // Servicio para operaciones con participaciones
    
    private static final Logger logger = LoggerFactory.getLogger(CsvService.class);

    // Método para leer un archivo CSV y devolver su contenido como un ArrayList en formato String
    public static List<String[]> leerCSV(String filePath) throws IOException {
        logger.info("Leyendo archivo CSV desde la ruta: " + filePath);
        List<String[]> data = new ArrayList<>(); // Lista para almacenar las líneas del CSV

        try (CSVReader reader = new CSVReader(new FileReader(filePath))) { // Usar try-with-resources para manejar la lectura del archivo
            String[] nextLine; // Variable para almacenar cada línea leída
            reader.readNext(); // Omitir la primera línea que es el encabezado

            // Leer el archivo línea por línea
            while ((nextLine = reader.readNext()) != null) {
                data.add(nextLine); // Añadir la línea leída a la lista
            }
            // Si la lectura es exitosa, devolver los datos leídos como un String
            return data;
        } catch (IOException e) { // Manejo de excepciones en caso de que ocurra un error al leer el archivo
            logger.error("Error al leer el archivo CSV: " + e.getMessage());
            // Si ocurre un error, devolver un mensaje de error
            return null;
        }
    }
    
    public ResponseEntity<String> procesarJugadores(String ruta) {
        try {
            List<String[]> jugadoresCsv = leerCSV(ruta);
            if (jugadoresCsv != null && !jugadoresCsv.isEmpty()) {
                // Llama al servicio para guardar los jugadores
                jugadorService.guardarJugadores(jugadoresCsv);
                return ResponseEntity.ok("Jugadores procesados correctamente.");
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("El archivo CSV de jugadores está vacío o no se pudo leer.");
            }
        } catch (IOException e) {
            logger.error("Error al procesar el archivo CSV de jugadores: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error al procesar el archivo CSV de jugadores.");
        }
    }

    public ResponseEntity<String> procesarEquipos(String ruta) {
        try {
            List<String[]> equiposCsv = leerCSV(ruta);
            if (equiposCsv != null && !equiposCsv.isEmpty()) {
                // Llama al servicio para guardar los equipos
                equipoService.guardarEquipos(equiposCsv);
                return ResponseEntity.ok("Equipos procesados correctamente.");
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("El archivo CSV de equipos está vacío o no se pudo leer.");
            }
        } catch (IOException e) {
            logger.error("Error al procesar el archivo CSV de equipos: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error al procesar el archivo CSV de equipos.");
        }
    }

    public ResponseEntity<String> procesarParticipaciones(String ruta) {
        try {
            List<String[]> participacionesCsv = leerCSV(ruta);
            if (participacionesCsv != null && !participacionesCsv.isEmpty()) {
                // Llama al servicio para guardar las participaciones
                participacionService.guardarParticipaciones(participacionesCsv);
                return ResponseEntity.ok("Participaciones procesadas correctamente.");
            } else {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("El archivo CSV de participaciones está vacío o no se pudo leer.");
            }
        } catch (IOException e) {
            logger.error("Error al procesar el archivo CSV de participaciones: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error al procesar el archivo CSV de participaciones.");
        }
    }
}

