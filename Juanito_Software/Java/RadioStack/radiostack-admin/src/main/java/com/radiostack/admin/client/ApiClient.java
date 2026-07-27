package com.radiostack.admin.client;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;

public class ApiClient {

    private final String baseUrl;
    private final HttpClient httpClient;
    private final ObjectMapper objectMapper;
    private String token;

    public ApiClient(String baseUrl) {
        this.baseUrl = baseUrl;
        this.httpClient = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(10)).build();
        this.objectMapper = new ObjectMapper();
    }

    public void setToken(String token) {
        this.token = token;
    }

    /**
     * Valor de la cabecera Authorization.
     *
     * El servidor devuelve el JWT pelado y el esquema "Bearer" se anade aqui,
     * que es donde corresponde: forma parte del protocolo HTTP, no del token.
     * Antes el prefijo venia incrustado en la propia cadena que enviaba el
     * servidor ("Bearer-demo-<id>"), asi que este cliente mandaba el token tal
     * cual y funcionaba por casualidad.
     */
    private String cabeceraAutorizacion() {
        return "Bearer " + token;
    }

    public String postJson(String path, Object body) throws Exception {
        String json = body == null ? "{}" : objectMapper.writeValueAsString(body);
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(10))
                .POST(HttpRequest.BodyPublishers.ofString(json));
        if (token != null) {
            builder.header("Authorization", cabeceraAutorizacion());
        }
        HttpResponse<String> response = httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 400) {
            throw new ApiException(response.statusCode(), response.body());
        }
        return response.body();
    }

    public String get(String path) throws Exception {
        HttpRequest.Builder builder = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + path))
                .timeout(Duration.ofSeconds(10))
                .GET();
        if (token != null) {
            builder.header("Authorization", cabeceraAutorizacion());
        }
        HttpResponse<String> response = httpClient.send(builder.build(), HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() >= 400) {
            throw new ApiException(response.statusCode(), response.body());
        }
        return response.body();
    }

    public LoginResult login(String email, String password) throws Exception {
        String body = postJson("/api/v1/auth/login", Map.of("email", email, "password", password));
        return objectMapper.readValue(body, LoginResult.class);
    }

    public static class ApiException extends RuntimeException {
        private final int statusCode;

        public ApiException(int statusCode, String body) {
            super("HTTP " + statusCode + ": " + body);
            this.statusCode = statusCode;
        }

        public int getStatusCode() {
            return statusCode;
        }
    }

    public static class LoginResult {
        public String token;
        public UserInfo usuario;

        public static class UserInfo {
            public Long id;
            public String nombre;
            public String email;
            public String rol;
        }
    }
}
