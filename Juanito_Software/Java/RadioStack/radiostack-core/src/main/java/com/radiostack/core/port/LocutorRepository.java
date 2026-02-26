package com.radiostack.core.port;

import com.radiostack.core.domain.Locutor;

import java.util.List;
import java.util.Optional;

public interface LocutorRepository {

    Locutor save(Locutor locutor);

    Optional<Locutor> findById(Long id);

    List<Locutor> findAll();
}

