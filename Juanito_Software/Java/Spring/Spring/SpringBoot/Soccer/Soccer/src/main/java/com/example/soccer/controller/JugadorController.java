/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.example.soccer.controller;

import com.example.soccer.dto.JugadorDTO;
import com.example.soccer.service.JugadorService;
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

/**
 *
 * @author User
 */

//Controlador para hacer llamadas a la API y usar las operaciones basicas, utilizando servicios

@RestController // Anotación que indica que esta clase es un controlador REST
@RequestMapping("/api") // Prefijo común para las rutas de este controlador


public class JugadorController {
    
    @Autowired
    private JugadorService jugadorService; // Servicio para operaciones relacionadas con jugadores

    
    // Endpoint para obtener todos los jugadores
    @GetMapping("/jugadores")
    public ResponseEntity<List<JugadorDTO>> getJugadores() {
            List<JugadorDTO> jugadoresDTOs = jugadorService.findAll(); // Llama al metodo para obtener todos los jugadores
            return ResponseEntity.ok(jugadoresDTOs); // Devuelve la lista de jugadores en el cuerpo de la respuesta
    }


    // Endpoint para obtener un jugador por ID
    @GetMapping("/jugadores/{id}")
    public ResponseEntity<JugadorDTO> getJugador(@PathVariable Long id) {
        JugadorDTO jugadorDTO = jugadorService.findById(id); // Llama al metodo para obtener un jugador por ID
        if (jugadorDTO != null) {
            return ResponseEntity.ok(jugadorDTO); // Retorna el jugador si fue encontrado
        } else {
            return ResponseEntity.notFound().build(); // Retorna 404 si no se encuentra
        }
    }

    // Endpoint para modificar un jugador por ID
    @PutMapping("/jugadores/{id}")
    public ResponseEntity<JugadorDTO> updateJugador(@PathVariable Long id, @RequestBody JugadorDTO jugador) {
        jugador.setId(id); // Asegúrate de que el ID del jugador se establezca correctamente
        JugadorDTO updatedJugador = jugadorService.updateJugador(jugador); // Llama al metodo para modificar el jugador
        if (updatedJugador != null) {
            return ResponseEntity.ok(updatedJugador); // Retorna el jugador actualizado
        } else {
            return ResponseEntity.notFound().build(); // Retorna 404 si no se encuentra
        }
    }

    // Endpoint para eliminar un jugador por ID
    @DeleteMapping("/jugadores/{id}")
    public ResponseEntity<Void> deleteJugador(@PathVariable Long id) {
        jugadorService.deleteJugador(id); // Llama al metodo para eliminar el jugador
        return ResponseEntity.noContent().build(); // Retorna 204 No Content
    }
}
