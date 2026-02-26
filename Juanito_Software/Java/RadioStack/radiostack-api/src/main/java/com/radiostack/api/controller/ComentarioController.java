package com.radiostack.api.controller;

import com.radiostack.api.dto.ComentarioDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.domain.EstadoComentario;
import com.radiostack.core.service.ComentarioService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class ComentarioController {

    private final ComentarioService comentarioService;

    public ComentarioController(ComentarioService comentarioService) {
        this.comentarioService = comentarioService;
    }

    @GetMapping("/api/v1/emisiones/{emisionId}/comentarios")
    public List<ComentarioDTO> listarPorEmision(@PathVariable Long emisionId) {
        return comentarioService.listarComentariosPorEmision(emisionId).stream()
                .map(DtoMapper::toComentarioDTO)
                .toList();
    }

    @PostMapping("/api/v1/emisiones/{emisionId}/comentarios")
    public ResponseEntity<ComentarioDTO> publicar(@PathVariable Long emisionId,
                                                  @RequestBody Map<String, String> body) {
        String autor = body.getOrDefault("autor", "Anónimo");
        String mensaje = body.get("mensaje");
        if (mensaje == null || mensaje.isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        var c = comentarioService.publicarComentario(emisionId, autor, mensaje);
        return ResponseEntity.status(HttpStatus.CREATED).body(DtoMapper.toComentarioDTO(c));
    }

    @PatchMapping("/api/v1/comentarios/{id}")
    public ResponseEntity<ComentarioDTO> cambiarEstado(@PathVariable Long id,
                                                        @RequestBody Map<String, String> body) {
        String estado = body.get("estado");
        if (estado == null) return ResponseEntity.badRequest().build();
        EstadoComentario ec = EstadoComentario.valueOf(estado);
        var c = comentarioService.cambiarEstadoComentario(id, ec);
        return ResponseEntity.ok(DtoMapper.toComentarioDTO(c));
    }
}
