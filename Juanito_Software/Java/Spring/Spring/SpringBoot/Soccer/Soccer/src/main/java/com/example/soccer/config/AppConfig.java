/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.example.soccer.config;

/**
 *
 * @author User
 */
import java.io.IOException;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.http.client.ClientHttpResponse;

import org.springframework.web.client.ResponseErrorHandler;
import org.springframework.web.client.RestTemplate;

@Configuration
public class AppConfig {
    private static final Logger logger = LoggerFactory.getLogger(AppConfig.class);
    @Bean
    public RestTemplate restTemplate(RestTemplateBuilder builder) {
        return builder
            .setConnectTimeout(Duration.ofMillis(5000))
            .setReadTimeout(Duration.ofMillis(5000))
            .errorHandler(new CustomResponseErrorHandler())
                .build();

    }
    private static class CustomResponseErrorHandler implements ResponseErrorHandler {

        @Override
        public boolean hasError(ClientHttpResponse response) throws IOException {
            HttpStatus statusCode = (HttpStatus) response.getStatusCode();
            return statusCode.series() == HttpStatus.Series.CLIENT_ERROR ||
                    statusCode.series() == HttpStatus.Series.SERVER_ERROR;
        }

        @Override
        public void handleError(ClientHttpResponse response) throws IOException {
            HttpStatus statusCode = (HttpStatus) response.getStatusCode();
            String statusText = response.getStatusText();
            String responseBody = new String(response.getBody().readAllBytes());

            // Log the error details
            logger.error("Error occurred: Status code: {}, Status text: {}, Response body: {}",
                    statusCode, statusText, responseBody);

            switch (statusCode.series()) {
                case CLIENT_ERROR:
                    // Manejo de errores 4xx
                    logger.warn("Client error: {}", statusText);
                    // Aquí puedes lanzar una excepción personalizada o realizar otras acciones
                    break;
                case SERVER_ERROR:
                    // Manejo de errores 5xx
                    logger.error("Server error: {}", statusText);
                    // Aquí también puedes lanzar una excepción personalizada o realizar otras acciones
                    break;
                default:
                    logger.error("Unexpected error: {}", statusText);
                    break;
            }
        }
    }
}
