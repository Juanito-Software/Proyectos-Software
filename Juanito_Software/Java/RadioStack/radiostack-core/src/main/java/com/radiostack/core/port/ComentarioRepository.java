package com.radiostack.core.port;

import com.radiostack.core.domain.Comentario;
import com.radiostack.core.domain.Emision;

import java.util.List;
import java.util.Optional;

public interface ComentarioRepository {

    Comentario save(Comentario comentario);

    Optional<Comentario> findById(Long id);

    List<Comentario> findByEmision(Emision emision);
}

