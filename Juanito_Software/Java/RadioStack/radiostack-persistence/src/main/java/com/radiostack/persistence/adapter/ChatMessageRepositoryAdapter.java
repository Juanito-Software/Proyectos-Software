package com.radiostack.persistence.adapter;

import com.radiostack.core.domain.ChatMessage;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.ChatMessageRepository;
import com.radiostack.persistence.entity.EmisionEntity;
import com.radiostack.persistence.mapper.DomainMapper;
import com.radiostack.persistence.repository.jpa.ChatMessageJpaRepository;
import com.radiostack.persistence.repository.jpa.EmisionJpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class ChatMessageRepositoryAdapter implements ChatMessageRepository {

    private final ChatMessageJpaRepository chatMessageJpaRepository;
    private final EmisionJpaRepository emisionJpaRepository;

    public ChatMessageRepositoryAdapter(ChatMessageJpaRepository chatMessageJpaRepository,
                                        EmisionJpaRepository emisionJpaRepository) {
        this.chatMessageJpaRepository = chatMessageJpaRepository;
        this.emisionJpaRepository = emisionJpaRepository;
    }

    @Override
    public ChatMessage save(ChatMessage message) {
        var entity = DomainMapper.toEntity(message);
        var saved = chatMessageJpaRepository.save(entity);
        return DomainMapper.toDomain(saved);
    }

    @Override
    public List<ChatMessage> findByEmision(Emision emision) {
        EmisionEntity emisionEntity = emisionJpaRepository.findById(emision.getId())
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada"));
        return chatMessageJpaRepository.findByEmision(emisionEntity)
                .stream()
                .map(DomainMapper::toDomain)
                .toList();
    }
}

