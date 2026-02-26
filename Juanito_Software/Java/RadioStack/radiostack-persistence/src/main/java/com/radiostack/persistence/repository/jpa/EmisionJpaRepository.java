package com.radiostack.persistence.repository.jpa;

import com.radiostack.persistence.entity.EmisionEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;

public interface EmisionJpaRepository extends JpaRepository<EmisionEntity, Long> {

    @Query("select e from EmisionEntity e where e.horaInicio >= :from and e.horaFin <= :to")
    List<EmisionEntity> findByRangoFechas(@Param("from") LocalDateTime from, @Param("to") LocalDateTime to);
}

