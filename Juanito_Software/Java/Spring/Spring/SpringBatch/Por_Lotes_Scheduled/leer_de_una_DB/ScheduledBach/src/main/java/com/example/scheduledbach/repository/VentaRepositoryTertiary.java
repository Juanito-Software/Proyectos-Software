package com.example.scheduledbach.repository;

import com.example.scheduledbach.models.Venta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface VentaRepositoryTertiary extends JpaRepository<Venta, Long> {
    // Aquí puedes agregar métodos personalizados si es necesario.
}