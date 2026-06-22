package com.example.BatchProcess.service;

import org.springframework.stereotype.Service;

import java.io.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FileWritterService {

    // Escribe los datos en archivos separados según el valor de una columna
    public void writeDataToFiles(String outputFolder, Map<String, List<String>> dividedData) throws IOException {
        for (Map.Entry<String, List<String>> entry : dividedData.entrySet()) {
            String key = entry.getKey();
            List<String> data = entry.getValue();
            try (BufferedWriter writer = createWriter(outputFolder, key)) {
                for (String line : data) {
                    writer.write(line);
                    writer.newLine();
                }
            }
        }
    }
    // Crea un escritor para un archivo determinado
    private BufferedWriter createWriter(String folder, String key) throws IOException {
        File file = new File(folder + "/" + key + ".csv");
        return new BufferedWriter(new FileWriter(file, true)); // Usar "true" para anexar al archivo
    }
}
