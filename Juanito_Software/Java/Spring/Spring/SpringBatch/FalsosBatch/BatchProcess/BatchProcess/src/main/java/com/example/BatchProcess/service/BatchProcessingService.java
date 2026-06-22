package com.example.BatchProcess.service;

import com.example.BatchProcess.service.FileProcessor;
import com.example.BatchProcess.service.FileReaderService;
import com.example.BatchProcess.service.FileWritterService;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.List;

@Service
public class BatchProcessingService {

    private final FileProcessor fileProcessor;

    // Constructor donde se inyecta el servicio de procesamiento de archivos
    public BatchProcessingService() {
        this.fileProcessor = new FileProcessor();
    }

    // Metodo que orquesta el procesamiento de archivos
    public void processBatch(String inputFilePath, String outputFolder) {
        try {
            // Validación del archivo (por ejemplo, si es un archivo CSV)
            if (!fileProcessor.validateFileFormat(inputFilePath)) {
                System.err.println("El archivo no tiene un formato válido (debe ser CSV).");
                return;
            }

            // Leer el archivo y obtener las líneas
            FileReaderService fileReader = new FileReaderService();
            List<String> records = fileReader.readFile(inputFilePath);

            // Validar la integridad de los datos (número de columnas, por ejemplo)
            int expectedColumnCount = 3;  // Cambia según el número esperado de columnas en el CSV
            if (!fileProcessor.validateDataIntegrity(records, expectedColumnCount)) {
                System.err.println("Los datos en el archivo no son válidos.");
                return;
            }

            // Dividir el archivo por la columna deseada (por ejemplo, la columna 0)
            int columnIndex = 2;  // Cambia según la columna por la que quieras dividir el archivo
            fileProcessor.divideFileByColumn(inputFilePath, columnIndex, outputFolder);

            System.out.println("Procesamiento de archivo completado.");

        } catch (IOException e) {
            System.err.println("Error durante el procesamiento del archivo: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
