package com.radiostack.persistence.repository.jpa;

import com.radiostack.persistence.entity.ComentarioEntity;
import com.radiostack.persistence.entity.EmisionEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ComentarioJpaRepository extends JpaRepository<ComentarioEntity, Long> {

    List<ComentarioEntity> findByEmision(EmisionEntity emision);
}

