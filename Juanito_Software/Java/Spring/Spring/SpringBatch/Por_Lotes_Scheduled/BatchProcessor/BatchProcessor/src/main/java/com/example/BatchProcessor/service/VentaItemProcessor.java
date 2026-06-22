package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Venta;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

@Component
public class VentaItemProcessor implements ItemProcessor<Venta, Venta> {

    @Override
    public Venta process(Venta venta) throws Exception {
        // Aquí podrías aplicar alguna lógica de transformación si es necesario
        // Por ejemplo, validar o modificar los datos antes de escribirlos
        return venta;
    }
}
