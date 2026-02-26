package com.radiostack.api.mapper;

import com.radiostack.api.dto.*;
import com.radiostack.core.domain.*;

import java.util.Collections;
import java.util.stream.Collectors;

public final class DtoMapper {

    private DtoMapper() {}

    public static ProgramaDTO toProgramaDTO(Programa p) {
        if (p == null) return null;
        ProgramaDTO dto = new ProgramaDTO();
        dto.setId(p.getId());
        dto.setNombre(p.getNombre());
        dto.setDescripcion(p.getDescripcion());
        dto.setCategoria(p.getCategoria());
        dto.setActivo(p.isActivo());
        if (p.getLocutores() != null) {
            dto.setLocutorIds(p.getLocutores().stream().map(Locutor::getId).collect(Collectors.toSet()));
        }
        return dto;
    }

    public static EmisionDTO toEmisionDTO(Emision e) {
        if (e == null) return null;
        EmisionDTO dto = new EmisionDTO();
        dto.setId(e.getId());
        if (e.getPrograma() != null) {
            dto.setProgramaId(e.getPrograma().getId());
            dto.setProgramaNombre(e.getPrograma().getNombre());
        }
        dto.setDiaSemana(e.getDiaSemana() != null ? e.getDiaSemana().name() : null);
        dto.setHoraInicio(e.getHoraInicio());
        dto.setHoraFin(e.getHoraFin());
        dto.setEstado(e.getEstado() != null ? e.getEstado().name() : null);
        return dto;
    }

    public static LocutorDTO toLocutorDTO(Locutor l) {
        if (l == null) return null;
        LocutorDTO dto = new LocutorDTO();
        dto.setId(l.getId());
        dto.setNombreArtistico(l.getNombreArtistico());
        if (l.getUsuario() != null) {
            dto.setUsuarioId(l.getUsuario().getId());
            dto.setUsuarioNombre(l.getUsuario().getNombre());
            dto.setUsuarioEmail(l.getUsuario().getEmail());
        }
        return dto;
    }

    public static UsuarioDTO toUsuarioDTO(Usuario u) {
        if (u == null) return null;
        UsuarioDTO dto = new UsuarioDTO();
        dto.setId(u.getId());
        dto.setNombre(u.getNombre());
        dto.setEmail(u.getEmail());
        dto.setRol(u.getRol() != null ? u.getRol().name() : null);
        dto.setActivo(u.isActivo());
        return dto;
    }

    public static ComentarioDTO toComentarioDTO(Comentario c) {
        if (c == null) return null;
        ComentarioDTO dto = new ComentarioDTO();
        dto.setId(c.getId());
        if (c.getEmision() != null) dto.setEmisionId(c.getEmision().getId());
        dto.setAutor(c.getAutor());
        dto.setMensaje(c.getMensaje());
        dto.setTimestamp(c.getTimestamp());
        dto.setEstado(c.getEstado() != null ? c.getEstado().name() : null);
        return dto;
    }

    public static ChatMessageDTO toChatMessageDTO(ChatMessage m) {
        if (m == null) return null;
        ChatMessageDTO dto = new ChatMessageDTO();
        dto.setId(m.getId());
        if (m.getEmision() != null) dto.setEmisionId(m.getEmision().getId());
        dto.setAlias(m.getAlias());
        dto.setContenido(m.getContenido());
        dto.setTimestamp(m.getTimestamp());
        return dto;
    }
}
