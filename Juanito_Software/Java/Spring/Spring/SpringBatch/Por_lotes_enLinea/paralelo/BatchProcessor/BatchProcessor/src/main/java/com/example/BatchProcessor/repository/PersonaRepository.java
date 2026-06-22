package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.Persona;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PersonaRepository extends JpaRepository<Persona, Long> {
    // No se necesita un metodo personalizado aquí por ahora
}

