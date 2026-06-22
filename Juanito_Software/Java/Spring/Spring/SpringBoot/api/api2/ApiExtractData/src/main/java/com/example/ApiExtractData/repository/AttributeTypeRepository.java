package com.example.ApiExtractData.repository;

import com.example.ApiExtractData.model.AttributeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface AttributeTypeRepository extends JpaRepository<AttributeType, Long> {
    // Aquí puedes definir métodos de consulta personalizados si los necesitas.
}

