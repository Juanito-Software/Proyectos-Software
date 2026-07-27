package com.example.BatchProcessor.service;

import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@Service
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
     * El orden importa: normalize() colapsa los ".." ANTES de comparar. Si se
     * comprobase primero, una entrada como "datos/../../etc/passwd" pasaría el
     * filtro y luego apuntaría fuera.
     */
    private static Path resolverDentroDeBase(String rutaRelativa) throws IOException {
        Path resuelta = BASE_DIR.resolve(rutaRelativa).normalize();
        if (!resuelta.startsWith(BASE_DIR)) {
            throw new IOException("Ruta fuera del directorio permitido: " + rutaRelativa);
        }
        return resuelta;
    }

    public List<String[]> leerCsvDesdeRuta(String inputFilePath) throws IOException {
        Path fichero = resolverDentroDeBase(inputFilePath);

        List<String[]> registros = new ArrayList<>();
        try (BufferedReader br = Files.newBufferedReader(fichero)) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] campos = linea.split(","); // Suponiendo CSV con coma como separador
                registros.add(campos);
            }
        } catch (IOException e) {
            throw new IOException("Error al leer el archivo CSV desde la ruta indicada", e);
        }
        return registros;
    }
}
