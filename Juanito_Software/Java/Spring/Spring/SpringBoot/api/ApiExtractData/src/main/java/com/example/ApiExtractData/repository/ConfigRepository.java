package com.example.ApiExtractData.repository;

import com.example.ApiExtractData.model.Config;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ConfigRepository extends JpaRepository<Config, Long> {
    List<Config> findByParentId(Long id);

    List<Config> findByParentIdIsNull();
    // Aquí puedes definir métodos de consulta personalizados si los necesitas.
}
