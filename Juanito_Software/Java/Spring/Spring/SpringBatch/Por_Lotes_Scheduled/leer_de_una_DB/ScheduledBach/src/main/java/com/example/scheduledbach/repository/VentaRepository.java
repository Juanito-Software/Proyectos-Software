package com.example.scheduledbach.repository;

import com.example.scheduledbach.models.Venta;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;


@Repository
public interface VentaRepository extends JpaRepository<Venta, Long> {
    // Puedes agregar métodos personalizados si los necesitas.
}

