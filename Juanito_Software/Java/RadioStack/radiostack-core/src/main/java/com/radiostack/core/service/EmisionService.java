package com.radiostack.core.service;

import com.radiostack.core.domain.Emision;

import java.util.Optional;

public interface EmisionService {

    Emision crearEmision(Emision emision);

    Emision actualizarEmision(Long id, Emision emision);

    Optional<Emision> obtenerEmision(Long id);
}
