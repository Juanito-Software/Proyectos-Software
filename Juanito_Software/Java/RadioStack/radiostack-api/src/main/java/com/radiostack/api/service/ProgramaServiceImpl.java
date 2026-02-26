package com.radiostack.api.service;

import com.radiostack.core.domain.Programa;
import com.radiostack.core.port.ProgramaRepository;
import com.radiostack.core.service.ProgramaService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
public class ProgramaServiceImpl implements ProgramaService {

    private final ProgramaRepository programaRepository;

    public ProgramaServiceImpl(ProgramaRepository programaRepository) {
        this.programaRepository = programaRepository;
    }

    @Override
    @Transactional
    public Programa crearPrograma(Programa programa) {
        programa.setId(null);
        return programaRepository.save(programa);
    }

    @Override
    @Transactional
    public Programa actualizarPrograma(Long id, Programa programa) {
        Programa existente = programaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Programa no encontrado: " + id));
        existente.setNombre(programa.getNombre());
        existente.setDescripcion(programa.getDescripcion());
        existente.setCategoria(programa.getCategoria());
        existente.setActivo(programa.isActivo());
        if (programa.getLocutores() != null) {
            existente.setLocutores(programa.getLocutores());
        }
        return programaRepository.save(existente);
    }

    @Override
    @Transactional
    public void eliminarPrograma(Long id) {
        programaRepository.deleteById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public Optional<Programa> obtenerPrograma(Long id) {
        return programaRepository.findById(id);
    }

    @Override
    @Transactional(readOnly = true)
    public List<Programa> listarProgramas() {
        return programaRepository.findAll();
    }
}
