package com.radiostack.persistence.adapter;

import com.radiostack.core.domain.Comentario;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.ComentarioRepository;
import com.radiostack.persistence.entity.EmisionEntity;
import com.radiostack.persistence.mapper.DomainMapper;
import com.radiostack.persistence.repository.jpa.ComentarioJpaRepository;
import com.radiostack.persistence.repository.jpa.EmisionJpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class ComentarioRepositoryAdapter implements ComentarioRepository {

    private final ComentarioJpaRepository comentarioJpaRepository;
    private final EmisionJpaRepository emisionJpaRepository;

    public ComentarioRepositoryAdapter(ComentarioJpaRepository comentarioJpaRepository,
                                       EmisionJpaRepository emisionJpaRepository) {
        this.comentarioJpaRepository = comentarioJpaRepository;
        this.emisionJpaRepository = emisionJpaRepository;
    }

    @Override
    public Comentario save(Comentario comentario) {
        var entity = DomainMapper.toEntity(comentario);
        var saved = comentarioJpaRepository.save(entity);
        return DomainMapper.toDomain(saved);
    }

    @Override
    public Optional<Comentario> findById(Long id) {
        return comentarioJpaRepository.findById(id).map(DomainMapper::toDomain);
    }

    @Override
    public List<Comentario> findByEmision(Emision emision) {
        EmisionEntity emisionEntity = emisionJpaRepository.findById(emision.getId())
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada"));
        return comentarioJpaRepository.findByEmision(emisionEntity)
                .stream()
                .map(DomainMapper::toDomain)
                .toList();
    }
}

