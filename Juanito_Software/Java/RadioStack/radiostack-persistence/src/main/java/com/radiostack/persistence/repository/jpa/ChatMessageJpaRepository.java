package com.radiostack.persistence.repository.jpa;

import com.radiostack.persistence.entity.ChatMessageEntity;
import com.radiostack.persistence.entity.EmisionEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface ChatMessageJpaRepository extends JpaRepository<ChatMessageEntity, Long> {

    List<ChatMessageEntity> findByEmision(EmisionEntity emision);
}

