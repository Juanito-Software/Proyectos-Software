package com.example.soccer.controller;

import com.example.soccer.service.ConversionesService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")// Define la ruta base para todos los endpoints en este controlador
public class ConversionesController {

    private final ConversionesService conversionesService;// Servicio que maneja la lógica de conversión

    // Constructor que inyecta el servicio de conversiones
    public ConversionesController(ConversionesService conversionesService) {
        this.conversionesService = conversionesService;
    }

    // Endpoint para convertir de decimal (String) a binario (Array de int)
    @GetMapping("/decimalStringBinarioArraInt")
    public ResponseEntity<int[]> decimalStringABinarioArraInt(@RequestParam String n) {

        // Llama al servicio para realizar la conversión y retorna el resultado
        return ResponseEntity.ok(conversionesService.convertirIPDecimalStringBinarioArraInt(n));
    }

    // Endpoint para convertir de binario(Array de int) a decimal (String)
    @GetMapping("/binarioArraIntDecimalString")
    public ResponseEntity<String> binarioArraIntADecimalString(@RequestParam  int[] n) {
        // Validación para asegurarse de que el array no esté vacío
        if (n == null || n.length == 0) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("El array de binarios no puede estar vacío.");
        }

        // Llama al servicio para realizar la conversión y retorna el resultado
        return ResponseEntity.ok(conversionesService.convertirIPbinarioArraIntADecimalString(n));
    }

    // Endpoint para convertir de decimal(String) a binario (String)
    @GetMapping("/decimalStringBinarioString")
    public ResponseEntity<String> decimalStringABinarioString(@RequestParam String n) {

        // Llama al servicio para realizar la conversión y retorna el resultado
        return ResponseEntity.ok(conversionesService.convertirIPdecimalStringBinarioString(n));
    }

    // Endpoint para convertir de binario(String) a decimal(String)
    @GetMapping("/binarioStringDecimalString")
    public ResponseEntity<String> binarioStringADecimalString(@RequestParam String n) {

        // Llama al servicio para realizar la conversión y retorna el resultado
        return ResponseEntity.ok(conversionesService.convertirIPbinarioStringDecimalString(n));
    }

    // Endpoint para convertir una dirección IP en formato de cadena a un número de 32 bits
    @GetMapping("/decimalStringBinarioLong32")
    public ResponseEntity<Long> decimalStringABinarioLong32(@RequestParam String n) {

        // Llama al servicio para realizar la conversión y retorna el resultado
        return ResponseEntity.ok(conversionesService.IpAddressStringToIpAddressLong32(n));
    }

    // Endpoint para convertir un número de 32 bits a una dirección IP en formato de cadena
    @GetMapping("/binarioLongDecimalString32")
    public ResponseEntity<String> binarioLongADecimalString32(@RequestParam long n) {

        // Llama al servicio para realizar la conversión y retorna el resultado
        return ResponseEntity.ok(conversionesService.IpAddressLong32ToIpAddressString(n));
    }
}
