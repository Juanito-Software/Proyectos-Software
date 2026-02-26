package com.radiostack.api.controller;

import com.radiostack.api.dto.EmisionDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.domain.DiaSemana;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.domain.EstadoEmision;
import com.radiostack.core.domain.Programa;
import com.radiostack.core.service.EmisionService;
import com.radiostack.core.service.ProgramaService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/emisiones")
public class EmisionController {

    private final EmisionService emisionService;
    private final ProgramaService programaService;

    public EmisionController(EmisionService emisionService, ProgramaService programaService) {
        this.emisionService = emisionService;
        this.programaService = programaService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<EmisionDTO> obtener(@PathVariable Long id) {
        return emisionService.obtenerEmision(id)
                .map(DtoMapper::toEmisionDTO)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<EmisionDTO> crear(@RequestBody EmisionDTO dto) {
        Emision e = new Emision();
        Programa p = new Programa();
        p.setId(dto.getProgramaId());
        e.setPrograma(p);
        e.setDiaSemana(DiaSemana.valueOf(dto.getDiaSemana()));
        e.setHoraInicio(dto.getHoraInicio());
        e.setHoraFin(dto.getHoraFin());
        e.setEstado(dto.getEstado() != null ? EstadoEmision.valueOf(dto.getEstado()) : EstadoEmision.PROGRAMADO);
        Emision creada = emisionService.crearEmision(e);
        return ResponseEntity.status(HttpStatus.CREATED).body(DtoMapper.toEmisionDTO(creada));
    }
}
