package com.radiostack.persistence.adapter;

import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.EmisionRepository;
import com.radiostack.persistence.entity.EmisionEntity;
import com.radiostack.persistence.mapper.DomainMapper;
import com.radiostack.persistence.repository.jpa.EmisionJpaRepository;
import com.radiostack.persistence.repository.jpa.ProgramaJpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public class EmisionRepositoryAdapter implements EmisionRepository {

    private final EmisionJpaRepository jpaRepository;
    private final ProgramaJpaRepository programaJpaRepository;

    public EmisionRepositoryAdapter(EmisionJpaRepository jpaRepository,
                                    ProgramaJpaRepository programaJpaRepository) {
        this.jpaRepository = jpaRepository;
        this.programaJpaRepository = programaJpaRepository;
    }

    @Override
    public Emision save(Emision emision) {
        EmisionEntity entity = DomainMapper.toEntity(emision);
        if (emision.getPrograma() != null && emision.getPrograma().getId() != null) {
            entity.setPrograma(programaJpaRepository.getReferenceById(emision.getPrograma().getId()));
        }
        EmisionEntity saved = jpaRepository.save(entity);
        return DomainMapper.toDomain(saved);
    }

    @Override
    public Optional<Emision> findById(Long id) {
        return jpaRepository.findById(id).map(DomainMapper::toDomain);
    }

    @Override
    public List<Emision> findByRangoFechas(LocalDateTime from, LocalDateTime to) {
        return jpaRepository.findByRangoFechas(from, to)
                .stream()
                .map(DomainMapper::toDomain)
                .toList();
    }

    @Override
    public List<Emision> findAll() {
        return jpaRepository.findAll().stream().map(DomainMapper::toDomain).toList();
    }
}
