package com.example.ApiExtractData.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.example.ApiExtractData.service.JsonManagerService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/json")
public class JsonController {

    private static final Logger log = LoggerFactory.getLogger(JsonController.class);

    // El controlador nos permite añadir datos en la base de datos usando los dtos y el assembler para convertir los dtos a entidad
    private final JsonManagerService jsonManagerService;

    public JsonController(JsonManagerService jsonManagerService) {
        this.jsonManagerService = jsonManagerService;
    }

    // Endpoint para extraer datos de la base de datos y generar JSON (directamente desde la entidad)
    @GetMapping("/extractJsonOfObjeto")
    public ResponseEntity<String> extractJsonOfObjeto() {
        try {
            String stringJson=jsonManagerService.serialize();
            return new ResponseEntity<>("Object serialized successfully in new json archive\n"+ stringJson, HttpStatus.OK);
        } catch (Exception e) {
            log.error("Error al serializar el objeto a JSON", e);
            return new ResponseEntity<>("Error on deserialice JSON. Consulte los logs del servidor.", HttpStatus.BAD_REQUEST);
        }
    }

    // Endpoint para leer un JSON y almacenar el objeto en la base de datos (directamente desde la entidad)
    @PostMapping("/storeObjectofJson")
    public ResponseEntity<String> storeObjectofJson(@RequestBody String json) {
        try {
            jsonManagerService.deserialize(json);
            return ResponseEntity.ok("Object deserialized of Json successfully in BD");
        } catch (Exception e) {
            log.error("Error al deserializar JSON", e);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }


    // Endpoint para extraer datos de la base de datos y generar JSON (usando los DTOs y Assemblers)
    @GetMapping("/extractJsonOfObjetoUsingDTO")
    public ResponseEntity<String> extractJsonOfObjetoUsingDTO() {
        try {
            String stringJson=jsonManagerService.serializeDTO();
            return new ResponseEntity<>("Object serialized successfully in new json archive usin DTOs\n"+ stringJson, HttpStatus.OK);
        } catch (Exception e) {
            log.error("Error al serializar el objeto a JSON usando DTOs", e);
            return new ResponseEntity<>("Error parsing JSON. Consulte los logs del servidor.", HttpStatus.BAD_REQUEST);
        }
    }

    // Endpoint para leer un JSON y almacenar el objeto en la base de datos (usando los DTOs y Assemblers)
    @PostMapping("/storeObjectofJsonUsingDTO")
    public ResponseEntity<String> storeObjectofJsonUsingDTO(@RequestBody String json) {
        try {
            jsonManagerService.deserializeDTO(json);
            return ResponseEntity.ok("Object deserialized of Json successfully in BD usin DTOs");
        } catch (Exception e) {
            log.error("Error al deserializar JSON usando DTOs", e);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
}


