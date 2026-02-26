package com.radiostack.core.service;

import com.radiostack.core.domain.Emision;

import java.time.LocalDate;
import java.util.List;

public interface ParrillaService {

    List<Emision> obtenerParrilla(LocalDate from, LocalDate to);
}

