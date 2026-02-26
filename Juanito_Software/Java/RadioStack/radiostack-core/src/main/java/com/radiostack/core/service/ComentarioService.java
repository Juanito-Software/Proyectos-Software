package com.radiostack.core.service;

import com.radiostack.core.domain.Comentario;
import com.radiostack.core.domain.EstadoComentario;

import java.util.List;

public interface ComentarioService {

    Comentario publicarComentario(Long emisionId, String autor, String mensaje);

    Comentario cambiarEstadoComentario(Long comentarioId, EstadoComentario nuevoEstado);

    List<Comentario> listarComentariosPorEmision(Long emisionId);
}

