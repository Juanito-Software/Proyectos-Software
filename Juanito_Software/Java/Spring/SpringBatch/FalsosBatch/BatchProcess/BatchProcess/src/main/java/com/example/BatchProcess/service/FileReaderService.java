package com.example.BatchProcess.service;

import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class FileReaderService {

    /**
     * Directorio base dentro del cual deben estar los ficheros que se leen.
     *
     * Por defecto es el directorio de trabajo. Se puede cambiar al arrancar:
     *     java -Dbatch.files.dir=D:/datos -jar app.jar
     */
    private static final Path BASE_DIR = Paths
            .get(System.getProperty("batch.files.dir", System.getProperty("user.dir")))
            .toAbsolutePath()
            .normalize();

    /**
     * Resuelve una ruta recibida del exterior y comprueba que no se escapa del
     * directorio permitido.
     *
     * normalize() colapsa los ".." antes de comparar; sin ese paso, una entrada
     * como "datos/../../etc/passwd" pasaría el filtro y luego apuntaría fuera.
     */
    static Path resolverDentroDeBase(String rutaRelativa) throws IOException {
        Path resuelta = BASE_DIR.resolve(rutaRelativa).normalize();
        if (!resuelta.startsWith(BASE_DIR)) {
            throw new IOException("Ruta fuera del directorio permitido: " + rutaRelativa);
        }
        return resuelta;
    }

    /** Lee el archivo y devuelve las líneas como una lista de cadenas. */
    public List<String> readFile(String filePath) throws IOException {
        Path fichero = resolverDentroDeBase(filePath);
        try (BufferedReader reader = Files.newBufferedReader(fichero)) {
            return reader.lines().toList();
        }
    }
}
