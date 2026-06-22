package com.example.ApiExtractData.repository;

import com.example.ApiExtractData.model.AttributeTypeValue;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AttributeTypeValueRepository extends JpaRepository<AttributeTypeValue, Long> {
    Optional<AttributeTypeValue> findById(Long id);

    // Aquí puedes definir métodos de consulta personalizados si los necesitas.
}

