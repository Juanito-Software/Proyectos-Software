package com.radiostack.api.service;

import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.EmisionRepository;
import com.radiostack.core.service.ParrillaService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.List;

@Service
public class ParrillaServiceImpl implements ParrillaService {

    private final EmisionRepository emisionRepository;

    public ParrillaServiceImpl(EmisionRepository emisionRepository) {
        this.emisionRepository = emisionRepository;
    }

    @Override
    @Transactional(readOnly = true)
    public List<Emision> obtenerParrilla(LocalDate from, LocalDate to) {
        return emisionRepository.findByRangoFechas(
                from.atStartOfDay(),
                to.atTime(LocalTime.MAX)
        );
    }
}
