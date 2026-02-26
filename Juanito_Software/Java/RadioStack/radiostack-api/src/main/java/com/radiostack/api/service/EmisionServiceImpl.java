package com.radiostack.api.service;

import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.EmisionRepository;
import com.radiostack.core.service.EmisionService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
public class EmisionServiceImpl implements EmisionService {

    private final EmisionRepository emisionRepository;

    public EmisionServiceImpl(EmisionRepository emisionRepository) {
        this.emisionRepository = emisionRepository;
    }

    @Override
    @Transactional
    public Emision crearEmision(Emision emision) {
        emision.setId(null);
        return emisionRepository.save(emision);
    }

    @Override
    @Transactional
    public Emision actualizarEmision(Long id, Emision emision) {
        Emision existente = emisionRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada: " + id));
        existente.setPrograma(emision.getPrograma());
        existente.setDiaSemana(emision.getDiaSemana());
        existente.setHoraInicio(emision.getHoraInicio());
        existente.setHoraFin(emision.getHoraFin());
        existente.setEstado(emision.getEstado());
        return emisionRepository.save(existente);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<Emision> obtenerEmision(Long id) {
        return emisionRepository.findById(id);
    }
}
