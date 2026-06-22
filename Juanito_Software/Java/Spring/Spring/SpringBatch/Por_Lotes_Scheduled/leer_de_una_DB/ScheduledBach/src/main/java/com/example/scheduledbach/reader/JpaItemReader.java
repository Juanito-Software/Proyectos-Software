package com.example.scheduledbach.reader;

import com.example.scheduledbach.models.Venta;
import com.example.scheduledbach.repository.VentaRepository;
import org.springframework.batch.item.ItemReader;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Iterator;

@Service
@Component
public class JpaItemReader implements ItemReader<Venta> {

    private final VentaRepository ventaRepository;  // Inyectamos el repositorio JPA
    private List<Venta> ventas;  // Lista que almacena todos los registros cargados
    private int currentIndex = 0;  // Índice para realizar la lectura de la lista

    @Autowired
    public JpaItemReader(VentaRepository ventaRepository) {
        this.ventaRepository = ventaRepository;
    }

    @Override
    public Venta read() throws Exception {
        // Si no se ha cargado la lista de ventas, la cargamos
        if (ventas == null) {
            cargarDatos();
        }

        // Si hemos leído todos los elementos, retornamos null
        if (ventas != null && currentIndex < ventas.size()) {
            return ventas.get(currentIndex++);  // Devolvemos el siguiente elemento y avanzamos el índice
        }

        return null;  // Retorna null cuando ya no hay más elementos
    }

    private void cargarDatos() {
        ventas = ventaRepository.findAll();  // Carga todas las ventas desde el repositorio
    }
}
