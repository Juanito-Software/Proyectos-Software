package com.example.BatchProcessor.reader;

import com.example.BatchProcessor.model.Venta;
import org.springframework.batch.item.ItemReader;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.FileReader;

@Component
public class CsvItemReader implements ItemReader<Venta> {

    private BufferedReader reader;
    private String currentLine;

    private static final String CSV_FILE_PATH = "classpath:ventas.csv";

    @Override
    public Venta read() throws Exception {
        if (reader == null) {
            reader = new BufferedReader(new FileReader(CSV_FILE_PATH));
        }

        if ((currentLine = reader.readLine()) != null) {
            String[] datos = currentLine.split(",");
            Long id = Long.parseLong(datos[0]);
            String producto = datos[1];
            int cantidad = Integer.parseInt(datos[2]);
            double precio = Double.parseDouble(datos[3]);
            return new Venta(id, producto, cantidad, precio);
        } else {
            reader.close();
            return null;
        }
    }
}