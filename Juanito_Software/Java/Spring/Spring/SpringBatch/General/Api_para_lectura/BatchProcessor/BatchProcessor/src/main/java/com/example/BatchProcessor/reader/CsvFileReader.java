package com.example.BatchProcessor.reader;

import com.example.BatchProcessor.model.Persona;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.core.io.FileSystemResource;
import org.springframework.stereotype.Component;


/**
 * Lector de archivo CSV que lee los registros de un archivo y los mapea a objetos FileRecord.
 * Esta clase es utilizada por Spring Batch para leer datos de archivos CSV y procesarlos por lotes.
 */
@Component
public class CsvFileReader extends FlatFileItemReader<Persona> {

    public CsvFileReader() {
        // Saltarse la primera línea (cabecera)
        setLinesToSkip(1);  // Esto hará que se ignore la primera línea del archivo CSV

        //setResource(new ClassPathResource("input.csv")); //implementacion para definir el archivo input desde la carpeta resources
        setLineMapper((line, lineNumber) -> {
            String[] fields = line.split(",");
            Persona persona = new Persona();
            persona.setNombreCompleto(fields[0]);
            persona.setEmpleo(fields[1]); // Campo de empleo
            return persona;
        });
    }

    // Metodo para establecer la ruta del archivo
    public void setFilePath(String filePath) {
        setResource(new FileSystemResource(filePath));  // Usar FileSystemResource para archivos del sistema
    }
}
