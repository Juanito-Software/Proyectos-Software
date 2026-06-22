package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.Venta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface VentaRepository extends JpaRepository<Venta, Long> {
    // Puedes agregar métodos personalizados si los necesitas.
}

