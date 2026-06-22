package com.example.scheduledbach.service;

import com.example.scheduledbach.models.Venta;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

@Service
@Component
public class VentaItemProcessor implements ItemProcessor<Venta, Venta> {

    @Override
    public Venta process(Venta venta) throws Exception {
        // Convertir cada atributo de la clase Venta a mayúsculas
        venta.setId(venta.getId());
        System.out.println(venta.getId());

        venta.setProducto(venta.getProducto().toUpperCase()); // Convierte el producto a mayúsculas
        System.out.println(venta.getProducto().toUpperCase());

        venta.setCantidad(venta.getCantidad());
        System.out.println(venta.getCantidad());

        venta.setPrecio(venta.getPrecio());
        System.out.println(venta.getPrecio());

        return venta;
    }
}
