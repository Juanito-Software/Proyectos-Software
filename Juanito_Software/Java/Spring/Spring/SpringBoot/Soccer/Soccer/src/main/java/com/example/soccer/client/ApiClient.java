/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.example.soccer.client;

/**
 *
 * @author User
 */

import com.example.soccer.model.Equipo;
import com.example.soccer.model.Jugador;
import com.example.soccer.model.Participacion;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

import java.util.List;

@Service
public class ApiClient {

    private final RestTemplate restTemplate;

    @Autowired
    public ApiClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    // Metodo para obtener un jugador por ID
    public Jugador getJugador(Long id) {
        String url = "http://localhost:8080/api/jugadores/" + id; // Asegúrate de que este es el endpoint correcto
        ResponseEntity<Jugador> response = restTemplate.getForEntity(url, Jugador.class);
        return response.getBody();
    }

    // Metodo para procesar jugadores
    public String procesarJugadores() {
        String url = "http://localhost:8080/procesar-jugadores"; // Asegúrate de que este es el endpoint correcto
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        return response.getBody();
    }
    
    // Metodo para obtener un equipo por ID
    public Equipo getEquipo(Long id) {
        String url = "http://localhost:8080/api/equipos/" + id; // Asegúrate de que este es el endpoint correcto
        ResponseEntity<Equipo> response = restTemplate.getForEntity(url, Equipo.class);
        return response.getBody();
    }
    
    // Metodo para procesar equipos
    public String procesarEquipos() {
        String url = "http://localhost:8080/procesar-equipos"; // Asegúrate de que este es el endpoint correcto
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        return response.getBody();
    }

    // Metodo para obtener una participación por ID
    public Participacion getParticipacion(Long id) {
        String url = "http://localhost:8080/api/participaciones/" + id; // Asegúrate de que este es el endpoint correcto
        ResponseEntity<Participacion> response = restTemplate.getForEntity(url, Participacion.class);
        return response.getBody();
    }
    
    // Metodo para procesar participaciones
    public String procesarParticipaciones() {
        String url = "http://localhost:8080/procesar-participaciones"; // Asegúrate de que este es el endpoint correcto
        ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
        return response.getBody();
    }
}
