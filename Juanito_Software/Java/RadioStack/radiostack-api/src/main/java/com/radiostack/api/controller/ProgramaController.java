package com.radiostack.api.controller;

import com.radiostack.api.dto.ProgramaDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.domain.Locutor;
import com.radiostack.core.domain.Programa;
import com.radiostack.core.port.LocutorRepository;
import com.radiostack.core.service.ProgramaService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/programas")
public class ProgramaController {

    private final ProgramaService programaService;
    private final LocutorRepository locutorRepository;

    public ProgramaController(ProgramaService programaService, LocutorRepository locutorRepository) {
        this.programaService = programaService;
        this.locutorRepository = locutorRepository;
    }

    @GetMapping
    public List<ProgramaDTO> listar() {
        return programaService.listarProgramas().stream()
                .map(DtoMapper::toProgramaDTO)
                .collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProgramaDTO> obtener(@PathVariable Long id) {
        return programaService.obtenerPrograma(id)
                .map(DtoMapper::toProgramaDTO)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<ProgramaDTO> crear(@RequestBody ProgramaDTO dto) {
        Programa p = toDomain(dto);
        Programa creado = programaService.crearPrograma(p);
        return ResponseEntity.status(HttpStatus.CREATED).body(DtoMapper.toProgramaDTO(creado));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ProgramaDTO> actualizar(@PathVariable Long id, @RequestBody ProgramaDTO dto) {
        Programa p = toDomain(dto);
        p.setId(id);
        if (dto.getLocutorIds() != null && !dto.getLocutorIds().isEmpty()) {
            p.setLocutores(dto.getLocutorIds().stream()
                    .map(locutorId -> locutorRepository.findById(locutorId).orElse(null))
                    .filter(l -> l != null)
                    .collect(Collectors.toSet()));
        }
        Programa actualizado = programaService.actualizarPrograma(id, p);
        return ResponseEntity.ok(DtoMapper.toProgramaDTO(actualizado));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminar(@PathVariable Long id) {
        programaService.eliminarPrograma(id);
        return ResponseEntity.noContent().build();
    }

    private Programa toDomain(ProgramaDTO dto) {
        Programa p = new Programa();
        p.setNombre(dto.getNombre());
        p.setDescripcion(dto.getDescripcion());
        p.setCategoria(dto.getCategoria());
        p.setActivo(dto.isActivo());
        if (dto.getLocutorIds() != null && !dto.getLocutorIds().isEmpty()) {
            p.setLocutores(dto.getLocutorIds().stream()
                    .map(locutorId -> locutorRepository.findById(locutorId).orElse(null))
                    .filter(l -> l != null)
                    .collect(Collectors.toSet()));
        }
        return p;
    }
}
