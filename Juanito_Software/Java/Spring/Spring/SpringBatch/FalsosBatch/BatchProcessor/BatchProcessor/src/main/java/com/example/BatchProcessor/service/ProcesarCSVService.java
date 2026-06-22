package com.example.BatchProcessor.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@Service
public class ProcesarCSVService {

    private final FileReaderService fileReaderService;
    private final FileWritterService fileWriterService;

    public ProcesarCSVService(FileReaderService fileReaderService, FileWritterService fileWriterService) {
        this.fileReaderService = fileReaderService;
        this.fileWriterService = fileWriterService;
    }

    public void procesarCsv(String inputFilePath) {
        try {
            // Leer los datos del archivo CSV desde la ruta proporcionada
            List<String[]> registros = fileReaderService.leerCsvDesdeRuta(inputFilePath);

            // Procesar los registros y guardarlos en la base de datos
            fileWriterService.procesarDatosYGuardar(registros);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

