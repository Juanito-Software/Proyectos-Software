package com.example.soccer.repository;

import com.example.soccer.model.Jugador;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;

@Repository
public interface JugadorRepository extends JpaRepository<Jugador, Long> {
    // Método para comprobar si ya existe un jugador con los mismos datos
    boolean existsByNombreAndApellidoAndFechaNac(String nombre, String apellido, LocalDate fechaNac);
}

