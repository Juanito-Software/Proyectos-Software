package com.example.BatchProcessor.service;

import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

@Service
public class FileReaderService {

    public List<String[]> leerCsvDesdeRuta(String inputFilePath) throws IOException {
        List<String[]> registros = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(inputFilePath))) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] campos = linea.split(","); // Suponiendo CSV con coma como separador
                registros.add(campos);
            }
        } catch (IOException e) {
            e.printStackTrace();
            throw new IOException("Error al leer el archivo CSV desde la ruta: " + inputFilePath);
        }
        return registros;
    }
}