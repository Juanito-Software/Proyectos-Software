package com.radiostack.api.controller;

import com.radiostack.api.dto.EmisionDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.service.ParrillaService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/v1/parrilla")
public class ParrillaController {

    private final ParrillaService parrillaService;

    public ParrillaController(ParrillaService parrillaService) {
        this.parrillaService = parrillaService;
    }

    @GetMapping
    public List<EmisionDTO> obtenerParrilla(
            @RequestParam(name = "from")
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate from,

            @RequestParam(name = "to")
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate to) {

        return parrillaService.obtenerParrilla(from, to)
                .stream()
                .map(DtoMapper::toEmisionDTO)
                .toList();
    }
}