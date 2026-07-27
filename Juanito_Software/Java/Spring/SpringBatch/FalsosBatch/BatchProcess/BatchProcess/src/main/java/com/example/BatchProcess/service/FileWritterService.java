package com.example.BatchProcess.service;

import org.springframework.stereotype.Service;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.Map;

public class FileWritterService {

    /** Escribe los datos en archivos separados según el valor de una columna. */
    public void writeDataToFiles(String outputFolder, Map<String, List<String>> dividedData) throws IOException {
        Path carpeta = FileReaderService.resolverDentroDeBase(outputFolder);
        Files.createDirectories(carpeta);

        for (Map.Entry<String, List<String>> entry : dividedData.entrySet()) {
            try (BufferedWriter writer = createWriter(carpeta, entry.getKey())) {
                for (String line : entry.getValue()) {
                    writer.write(line);
                    writer.newLine();
                }
            }
        }
    }

    /**
     * Crea un escritor para el fichero correspondiente a una clave.
     *
     * La clave procede de una columna del CSV de entrada, es decir, de datos
     * que controla quien sube el fichero. Sin sanear, un valor como
     * "../../config" haría que se escribiese fuera de la carpeta de salida.
     */
    private BufferedWriter createWriter(Path carpeta, String key) throws IOException {
        String nombreSeguro = key.replaceAll("[^A-Za-z0-9._-]", "_");
        if (nombreSeguro.isBlank() || nombreSeguro.startsWith(".")) {
            throw new IOException("Nombre de fichero no válido a partir de la clave: " + key);
        }

        Path fichero = carpeta.resolve(nombreSeguro + ".csv").normalize();
        if (!fichero.startsWith(carpeta)) {
            throw new IOException("Ruta de salida fuera de la carpeta permitida: " + key);
        }

        return Files.newBufferedWriter(fichero,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }
}
