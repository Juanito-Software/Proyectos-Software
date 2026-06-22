package com.example.BatchProcessor.reader;

import com.example.BatchProcessor.model.FileRecord;
import org.springframework.batch.item.file.FlatFileItemReader;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.stereotype.Component;


/**
 * Lector de archivo CSV que lee los registros de un archivo y los mapea a objetos FileRecord.
 * Esta clase es utilizada por Spring Batch para leer datos de archivos CSV y procesarlos por lotes.
 */
@Component
public class CsvFileReader extends FlatFileItemReader<FileRecord> {
    public CsvFileReader() {
        // Saltarse la primera línea (cabecera)
        setLinesToSkip(1);  // Esto hará que se ignore la primera línea del archivo CSV

        //setResource(new ClassPathResource("input.csv")); //implementacion para definir el archivo input desde la carpeta resources
        setLineMapper((line, lineNumber) -> {
            String[] fields = line.split(",");
            FileRecord record = new FileRecord();
            record.setNombre(fields[0]);
            record.setApellido(fields[1]);
            record.setNombreEmpleo(fields[2]); // Campo de empleo
            return record;
        });
    }

    // Metodo para establecer la ruta del archivo
    public void setFilePath(String filePath) {
        setResource(new FileSystemResource(filePath));  // Usar FileSystemResource para archivos del sistema
    }
}
