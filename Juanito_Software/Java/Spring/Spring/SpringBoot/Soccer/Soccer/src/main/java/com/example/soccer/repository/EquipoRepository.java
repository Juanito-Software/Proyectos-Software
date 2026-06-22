package com.example.soccer.repository;

import com.example.soccer.model.Equipo;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;

@Repository
public interface EquipoRepository extends JpaRepository<Equipo, Long> {
    // Método para comprobar si ya existe un equipo con los mismos datos
    boolean existsByNombreAndCiudad(String nombre, String ciudad);
}
