package com.radiostack.persistence.adapter;

import com.radiostack.core.domain.Programa;
import com.radiostack.core.port.ProgramaRepository;
import com.radiostack.persistence.mapper.DomainMapper;
import com.radiostack.persistence.repository.jpa.ProgramaJpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class ProgramaRepositoryAdapter implements ProgramaRepository {

    private final ProgramaJpaRepository jpaRepository;

    public ProgramaRepositoryAdapter(ProgramaJpaRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
    }

    @Override
    public Programa save(Programa programa) {
        var entity = DomainMapper.toEntity(programa);
        var saved = jpaRepository.save(entity);
        return DomainMapper.toDomain(saved);
    }

    @Override
    public Optional<Programa> findById(Long id) {
        return jpaRepository.findById(id).map(DomainMapper::toDomain);
    }

    @Override
    public List<Programa> findAll() {
        return jpaRepository.findAll().stream().map(DomainMapper::toDomain).toList();
    }

    @Override
    public void deleteById(Long id) {
        jpaRepository.deleteById(id);
    }
}

