package com.example.BatchProcessor.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springdoc.core.models.GroupedOpenApi;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Documentación OpenAPI/Swagger servida por springdoc.
 *
 * <p>La interfaz queda en {@code /swagger-ui/index.html} y la especificación en
 * {@code /v3/api-docs}. Desde ahí se puede probar {@code POST /batch/run}
 * rellenando los parámetros {@code reader}, {@code processor},
 * {@code writer} y, si hace falta, {@code transactionManager}.
 *
 * @author User
 */
@Configuration
public class SwaggerConfig {

    /**
     * Grupo único {@code public-api} que incluye todas las rutas.
     *
     * @return definición del grupo para springdoc
     */
    @Bean
    public GroupedOpenApi publicApi() {
        return GroupedOpenApi.builder()
                .group("public-api")
                .pathsToMatch("/**") // Ajusta las rutas según sea necesario
                .build();
    }

    /**
     * Metadatos que muestra la cabecera de Swagger (título, versión,
     * descripción).
     *
     * @return especificación OpenAPI base
     */
    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Generic Entity Spring Batch Processor API")
                        .version("1.0")
                        .description("API for Generic Entity Processing")); // Ajusta la información según tu proyecto
    }
}