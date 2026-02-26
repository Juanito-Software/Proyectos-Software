package com.radiostack.core.port;

import com.radiostack.core.domain.Emision;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface EmisionRepository {

    Emision save(Emision emision);

    Optional<Emision> findById(Long id);

    List<Emision> findByRangoFechas(LocalDateTime from, LocalDateTime to);

    List<Emision> findAll();
}

