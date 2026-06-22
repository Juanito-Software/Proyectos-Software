package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.GenericEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface GenericRepository<T extends GenericEntity, ID> extends JpaRepository<T, ID> {
    // Métodos adicionales si es necesario
}
