package com.example.ApiExtractData.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.example.ApiExtractData.service.JsonManagerService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * Controlador para gestionar las operaciones relacionadas con JSON.
 * Este controlador permite interactuar con el servicio {@link JsonManagerService} para serializar datos
 * desde la base de datos a formato JSON.
 */

@RestController
@RequestMapping("/api/json")
public class JsonController {

    private static final Logger log = LoggerFactory.getLogger(JsonController.class);

    /**
     * El servicio que maneja la serialización de los datos JSON.
     */
    private final JsonManagerService jsonManagerService;

    /**
     * Constructor para inicializar el controlador con el servicio {@link JsonManagerService}.
     *
     * @param jsonManagerService El servicio para manejar la conversión de datos a JSON.
     */
    public JsonController(JsonManagerService jsonManagerService) {
        this.jsonManagerService = jsonManagerService;
    }

    /**
     * Endpoint para extraer datos de la base de datos y generar un archivo JSON.
     * Este endpoint serializa los datos almacenados en la base de datos a formato JSON y los devuelve en la respuesta.
     *
     * @return Una respuesta {@link ResponseEntity} con el JSON generado si es exitoso, o un mensaje de error si ocurre una excepción.
     */
    @GetMapping("/extractJsonOfObjeto")
    public ResponseEntity<String> extractJsonOfObjeto() {
        try {
            String stringJson = jsonManagerService.serialize();// Llama al servicio para serializar los datos a JSON
            // Retorna el JSON serializado con un mensaje de éxito
            return new ResponseEntity<>("Object serialized successfully in new json archive\n" + stringJson, HttpStatus.OK);
        } catch (Exception e) {
            log.error("Error al serializar el objeto a JSON", e);
            return new ResponseEntity<>("Error on serialice JSON. Consulte los logs del servidor.", HttpStatus.BAD_REQUEST);
        }
    }

    /*// Endpoint para extraer datos de la base de datos y generar JSON (usando los DTOs y Assemblers)
    @GetMapping("/extractJsonOfObjetoUsingDTO")
    public ResponseEntity<String> extractJsonOfObjetoUsingDTO() {
        try {
            String stringJson=jsonManagerService.serializeDTO();
            return new ResponseEntity<>("Object serialized successfully in new json archive usin DTOs\n"+ stringJson, HttpStatus.OK);
        } catch (Exception e) {
            return new ResponseEntity<>("Error parsing JSON: " + e.getMessage(), HttpStatus.BAD_REQUEST);
        }
    }*/
}





