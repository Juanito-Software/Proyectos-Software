package com.radiostack.api.service;

import com.radiostack.core.domain.Comentario;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.domain.EstadoComentario;
import com.radiostack.core.port.ComentarioRepository;
import com.radiostack.core.port.EmisionRepository;
import com.radiostack.core.service.ComentarioService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class ComentarioServiceImpl implements ComentarioService {

    private final ComentarioRepository comentarioRepository;
    private final EmisionRepository emisionRepository;

    public ComentarioServiceImpl(ComentarioRepository comentarioRepository,
                                 EmisionRepository emisionRepository) {
        this.comentarioRepository = comentarioRepository;
        this.emisionRepository = emisionRepository;
    }

    @Override
    @Transactional
    public Comentario publicarComentario(Long emisionId, String autor, String mensaje) {
        Emision emision = emisionRepository.findById(emisionId)
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada: " + emisionId));
        Comentario c = new Comentario();
        c.setEmision(emision);
        c.setAutor(autor);
        c.setMensaje(mensaje);
        c.setTimestamp(LocalDateTime.now());
        c.setEstado(EstadoComentario.VISIBLE);
        return comentarioRepository.save(c);
    }

    @Override
    @Transactional
    public Comentario cambiarEstadoComentario(Long comentarioId, EstadoComentario nuevoEstado) {
        Comentario c = comentarioRepository.findById(comentarioId)
                .orElseThrow(() -> new IllegalArgumentException("Comentario no encontrado: " + comentarioId));
        c.setEstado(nuevoEstado);
        return comentarioRepository.save(c);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Comentario> listarComentariosPorEmision(Long emisionId) {
        Emision emision = emisionRepository.findById(emisionId)
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada: " + emisionId));
        return comentarioRepository.findByEmision(emision);
    }
}
