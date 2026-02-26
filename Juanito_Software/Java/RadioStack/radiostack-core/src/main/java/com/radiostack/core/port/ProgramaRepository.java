package com.radiostack.core.port;

import com.radiostack.core.domain.Programa;

import java.util.List;
import java.util.Optional;

public interface ProgramaRepository {

    Programa save(Programa programa);

    Optional<Programa> findById(Long id);

    List<Programa> findAll();

    void deleteById(Long id);
}

