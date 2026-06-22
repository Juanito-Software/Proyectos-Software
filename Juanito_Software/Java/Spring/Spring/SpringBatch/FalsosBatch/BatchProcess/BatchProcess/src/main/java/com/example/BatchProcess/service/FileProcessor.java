package com.example.BatchProcess.service;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FileProcessor {

    private final FileReaderService fileReader;
    private final FileWritterService fileWritter;

    // Constructor
    public FileProcessor() {
        this.fileReader = new FileReaderService();
        this.fileWritter = new FileWritterService();
    }

    // Divide el archivo según una columna y escribe en archivos separados
    public void divideFileByColumn(String inputFilePath, int columnIndex, String outputFolder) throws IOException {
        // Leer las líneas del archivo usando FileReader
        List<String> lines = fileReader.readFile(inputFilePath);

        // Dividir las líneas por el valor de la columna especificada
        Map<String, List<String>> dividedData = new HashMap<>();
        for (String line : lines) {
            String[] columns = line.split(",");
            String key = columns[columnIndex]; // Usar el valor de la columna como clave
            dividedData.computeIfAbsent(key, k -> new ArrayList<>()).add(line);
        }

        // Escribir las líneas divididas en archivos separados
        fileWritter.writeDataToFiles(outputFolder, dividedData);
    }

    // Valida si el archivo tiene un formato adecuado (por ejemplo, si es un CSV)
    public boolean validateFileFormat(String filePath) {
        // Validación básica para verificar si el archivo es un CSV
        return filePath.endsWith(".csv");
    }

    // Valida la integridad de los datos, verificando el número de columnas
    public boolean validateDataIntegrity(List<String> records, int expectedColumnCount) {
        // Validación de registros para asegurarse de que tengan el número correcto de columnas
        for (String record : records) {
            String[] columns = record.split(",");
            if (columns.length != expectedColumnCount) {
                return false;
            }
        }
        return true;
    }
}

