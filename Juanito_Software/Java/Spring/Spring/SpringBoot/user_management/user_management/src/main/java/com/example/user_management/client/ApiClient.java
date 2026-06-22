/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.example.user_management.client;

/**
 *
 * @author User
 */
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;
import com.example.user_management.model.Usuario;

@Service
public class ApiClient {
    
    private final RestTemplate restTemplate;

    @Autowired
    public ApiClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    
    public Usuario getUsuario(Long id) {
        String url = "http://localhost:8080/api/usuarios/" + id;
        ResponseEntity<Usuario> response = restTemplate.getForEntity(url, Usuario.class);
        return response.getBody();
    }
}