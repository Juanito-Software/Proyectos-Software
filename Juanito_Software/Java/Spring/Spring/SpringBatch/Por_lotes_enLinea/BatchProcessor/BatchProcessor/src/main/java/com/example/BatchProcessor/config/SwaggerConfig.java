package com.example.BatchProcessor.config;

/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */

/**
 * Configuración de Swagger para la generación de documentación de la API.
 * Esta clase configura el grupo de la API y el paquete a escanear para generar la documentación
 * con OpenAPI para los controladores de la aplicación.
 */

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean(name = "api")
    public GroupedOpenApi api() {
        return GroupedOpenApi.builder()
                .group("batch-processor")
                .packagesToScan("com.example.BatchProcessor.controller")
                .build();
    }
}