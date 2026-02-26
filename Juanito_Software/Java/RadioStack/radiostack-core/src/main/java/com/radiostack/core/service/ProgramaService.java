package com.radiostack.core.service;

import com.radiostack.core.domain.Programa;

import java.util.List;
import java.util.Optional;

public interface ProgramaService {

    Programa crearPrograma(Programa programa);

    Programa actualizarPrograma(Long id, Programa programa);

    void eliminarPrograma(Long id);

    Optional<Programa> obtenerPrograma(Long id);

    List<Programa> listarProgramas();
}

