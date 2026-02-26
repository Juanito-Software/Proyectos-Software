package com.radiostack.stream;

import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;

/**
 * Implementación placeholder del servicio de metadatos de streaming.
 * Sustituir por integración real con Icecast (HTTP API) o SHOUTcast.
 */
public class StreamMetadataServiceImpl implements StreamMetadataService {

    private final AtomicReference<String> currentTitle = new AtomicReference<>();

    @Override
    public void setCurrentTitle(String title) {
        currentTitle.set(title);
    }

    @Override
    public Optional<String> getCurrentTitle() {
        return Optional.ofNullable(currentTitle.get());
    }

    @Override
    public void connect(String streamUrl, String mountPoint, String password) {
        // TODO: abrir conexión con servidor de streaming y enviar metadatos
    }
}
