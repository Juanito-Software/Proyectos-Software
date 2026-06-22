package com.example.soccer.repository;

import com.example.soccer.model.Equipo;
import com.example.soccer.model.Participacion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;

@Repository
public interface ParticipacionRepository extends JpaRepository<Participacion, Long> {

    // Método para verificar si ya existe un dorsal en un equipo en fechas que se solapan
    @Query("SELECT CASE WHEN COUNT(p) > 0 THEN true ELSE false END " +
            "FROM participacion p " +
            "WHERE p.equipo = :equipo " +
            "AND p.dorsal = :dorsal " +
            "AND (p.fechaInicio <= :fechaFin AND p.fechaFin >= :fechaInicio)")
    boolean existsByEquipoAndDorsalAndFechas(@Param("equipo") Equipo equipo,
                                             @Param("dorsal") int dorsal,
                                             @Param("fechaInicio") LocalDate fechaInicio,
                                             @Param("fechaFin") LocalDate fechaFin);


}


