package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.Persona;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PersonaRepository extends JpaRepository<Persona, Long> {
    boolean existsByNombreCompleto(String nombreCompleto);

    Optional<Persona> findByNombreCompleto(String nombreCompleto);
}

