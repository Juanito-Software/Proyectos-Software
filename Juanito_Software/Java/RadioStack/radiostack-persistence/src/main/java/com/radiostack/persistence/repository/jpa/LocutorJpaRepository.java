package com.radiostack.persistence.repository.jpa;

import com.radiostack.persistence.entity.LocutorEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LocutorJpaRepository extends JpaRepository<LocutorEntity, Long> {
}

