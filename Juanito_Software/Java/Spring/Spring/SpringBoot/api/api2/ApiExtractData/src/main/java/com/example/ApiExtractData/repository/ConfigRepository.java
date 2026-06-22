package com.example.ApiExtractData.repository;

import com.example.ApiExtractData.model.Config;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ConfigRepository extends JpaRepository<Config, Long> {
    // Aquí puedes definir métodos de consulta personalizados si los necesitas.
}
