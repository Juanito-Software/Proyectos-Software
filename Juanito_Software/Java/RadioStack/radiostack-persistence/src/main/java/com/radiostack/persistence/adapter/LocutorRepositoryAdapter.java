package com.radiostack.persistence.adapter;

import com.radiostack.core.domain.Locutor;
import com.radiostack.core.port.LocutorRepository;
import com.radiostack.persistence.entity.LocutorEntity;
import com.radiostack.persistence.mapper.DomainMapper;
import com.radiostack.persistence.repository.jpa.LocutorJpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public class LocutorRepositoryAdapter implements LocutorRepository {

    private final LocutorJpaRepository jpaRepository;

    public LocutorRepositoryAdapter(LocutorJpaRepository jpaRepository) {
        this.jpaRepository = jpaRepository;
    }

    @Override
    public Locutor save(Locutor locutor) {
        LocutorEntity entity = DomainMapper.toEntity(locutor);
        LocutorEntity saved = jpaRepository.save(entity);
        return DomainMapper.toDomain(saved);
    }

    @Override
    public Optional<Locutor> findById(Long id) {
        return jpaRepository.findById(id).map(DomainMapper::toDomain);
    }

    @Override
    public List<Locutor> findAll() {
        return jpaRepository.findAll().stream().map(DomainMapper::toDomain).toList();
    }
}

