package com.radiostack.persistence.repository.jpa;

import com.radiostack.persistence.entity.ProgramaEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProgramaJpaRepository extends JpaRepository<ProgramaEntity, Long> {
}

