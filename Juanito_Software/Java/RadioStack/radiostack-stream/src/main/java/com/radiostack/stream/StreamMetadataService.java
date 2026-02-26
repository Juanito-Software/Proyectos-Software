package com.radiostack.stream;

import java.util.Optional;

/**
 * Servicio de metadatos de emisión para integración con servidor de streaming
 * (Icecast / SHOUTcast). En una implementación futura:
 * - Actualizar título/artista que muestra el reproductor
 * - Sincronizar con la emisión en curso en radiostack-api
 */
public interface StreamMetadataService {

    /**
     * Establece el título actual del stream (ej. nombre del programa en vivo).
     */
    void setCurrentTitle(String title);

    /**
     * Obtiene el título actual si hay emisión activa.
     */
    Optional<String> getCurrentTitle();

    /**
     * Conecta con el servidor de streaming (URL del admin, mont point, etc.).
     * Placeholder para integración Icecast/SHOUTcast.
     */
    void connect(String streamUrl, String mountPoint, String password);
}
