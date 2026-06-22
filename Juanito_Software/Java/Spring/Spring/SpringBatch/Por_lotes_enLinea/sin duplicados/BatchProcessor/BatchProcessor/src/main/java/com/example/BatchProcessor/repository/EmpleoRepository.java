package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.Empleo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface EmpleoRepository extends JpaRepository<Empleo, Long> {

    // Metodo personalizado para buscar empleo por su nombre
    Optional<Empleo> findByNombreEmpleo(String nombreEmpleo);
}

