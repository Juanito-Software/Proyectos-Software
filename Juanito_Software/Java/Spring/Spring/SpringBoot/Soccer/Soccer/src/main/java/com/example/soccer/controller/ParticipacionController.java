/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.example.soccer.controller;

import com.example.soccer.dto.ParticipacionDTO;
import com.example.soccer.service.ParticipacionService;
import java.util.List;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 *
 * @author User
 */

//Controlador para hacer llamadas a la API y usar las operaciones basicas, utilizando servicios

@RestController // Anotación que indica que esta clase es un controlador REST
@RequestMapping("/api") // Prefijo común para las rutas de este controlador

public class ParticipacionController {
    
    @Autowired
    private ParticipacionService participacionService; // Servicio para operaciones relacionadas con participaciones
    
    // Endpoint para obtener todas las participaciones
    @GetMapping("/participaciones")
    public ResponseEntity<List<ParticipacionDTO>> getParticipaciones() {
        List<ParticipacionDTO> participacionesDTOs = participacionService.findAll(); // Llama al metodo para obtener todas las participaciones
        return ResponseEntity.ok(participacionesDTOs); // Devuelve la lista de participaciones en el cuerpo de la respuesta
    }

    // Endpoint para obtener una participación por ID
    @GetMapping("/participaciones/{id}")
    public ResponseEntity<ParticipacionDTO> getParticipacion(@PathVariable Long id) {
        ParticipacionDTO participacionDTO = participacionService.findById(id); // Llama al metodo para obtener una participación por ID
        if (participacionDTO != null) {
            return ResponseEntity.ok(participacionDTO); // Retorna la participación si fue encontrada
        } else {
            return ResponseEntity.notFound().build(); // Retorna 404 si no se encuentra
        }
    }


    // Endpoint para modificar una participación por ID
    @PutMapping("/participaciones/{id}")
    public ResponseEntity<Optional<ParticipacionDTO>> updateParticipacion(@PathVariable Long id, @RequestBody ParticipacionDTO participacionDTO) {
        participacionDTO.setId(id); // Asegúrate de que el ID de la participación se establezca correctamente
        Optional<ParticipacionDTO> updatedParticipacion = participacionService.updateParticipacion(participacionDTO); // Llama al metodo para modificar la participación
        if (updatedParticipacion != null) {
            return ResponseEntity.ok(updatedParticipacion); // Retorna la participación actualizada
        } else {
            return ResponseEntity.notFound().build(); // Retorna 404 si no se encuentra
        }
    }

    // Endpoint para eliminar una participación por ID
    @DeleteMapping("/participaciones/{id}")
    public void deleteParticipacion(@PathVariable Long id) {
        participacionService.deleteParticipacion(id); // Llama al metodo para eliminar la participación
    }
}
