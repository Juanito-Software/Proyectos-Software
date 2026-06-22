/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.example.soccer.controller;

import com.example.soccer.dto.EquipoDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.service.EquipoService;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.Optional; // Asegúrate de importar Optional si lo estás usando

/**
 *
 * @author User
 */

//Controlador para hacer llamadas a la API y usar las operaciones basicas, utilizando servicios

@RestController // Anotación que indica que esta clase es un controlador REST
@RequestMapping("/api") // Prefijo común para las rutas de este controlador

public class EquipoController {
    
    @Autowired
    private EquipoService equipoService; // Servicio para operaciones relacionadas con equipos
    
    // Endpoint para obtener todos los equipos
    @GetMapping("/equipos")
    public ResponseEntity<List<EquipoDTO>> getEquipos() {
        return ResponseEntity.ok(equipoService.findAll()); // Llama al servicio que retorna DTOs
    }

    // Endpoint para obtener un equipo por ID
    @GetMapping("/equipos/{id}")
    public ResponseEntity<EquipoDTO> getEquipo(@PathVariable Long id) {
        return equipoService.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build()); // Retorna 404 si no se encuentra
    }

    // Endpoint para modificar un equipo por ID
    @PutMapping("/equipos/{id}")
    public ResponseEntity<EquipoDTO> updateEquipo(@PathVariable Long id, @RequestBody EquipoDTO equipoDTO) {
        equipoDTO.setId(id); // Asegúrate de que el ID del equipo se establezca correctamente
        return ResponseEntity.of(equipoService.updateEquipo(equipoDTO)); // Devuelve el equipo actualizado o 404
    }

    // Endpoint para eliminar un equipo por ID
    @DeleteMapping("/equipos/{id}")
    public ResponseEntity<Void> deleteEquipo(@PathVariable Long id) {
        equipoService.deleteEquipo(id);
        return ResponseEntity.noContent().build(); // Retorna 204 No Content
    }
}