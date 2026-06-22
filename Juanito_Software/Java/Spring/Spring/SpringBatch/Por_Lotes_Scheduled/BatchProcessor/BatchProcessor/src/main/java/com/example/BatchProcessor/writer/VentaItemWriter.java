package com.example.BatchProcessor.writer;

import com.example.BatchProcessor.model.Venta;
import com.example.BatchProcessor.repository.VentaRepository;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class VentaItemWriter implements ItemWriter<Venta> {


    private final VentaRepository ventaRepository;

    public VentaItemWriter(VentaRepository ventaRepository) {
        this.ventaRepository = ventaRepository;
    }

    @Override
    public void write(Chunk<? extends Venta> chunk) throws Exception {
        ventaRepository.saveAll(chunk);
    }
}
