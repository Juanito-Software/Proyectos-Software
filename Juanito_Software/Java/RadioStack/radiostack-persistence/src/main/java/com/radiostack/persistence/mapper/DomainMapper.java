package com.radiostack.persistence.mapper;

import com.radiostack.core.domain.*;
import com.radiostack.persistence.entity.*;

import java.util.stream.Collectors;

public final class DomainMapper {

    private DomainMapper() {
    }

    public static Usuario toDomain(UsuarioEntity entity) {
        if (entity == null) return null;
        return new Usuario(
                entity.getId(),
                entity.getNombre(),
                entity.getEmail(),
                entity.getPasswordHash(),
                entity.getRol(),
                entity.isActivo()
        );
    }

    public static UsuarioEntity toEntity(Usuario usuario) {
        if (usuario == null) return null;
        UsuarioEntity entity = new UsuarioEntity();
        entity.setId(usuario.getId());
        entity.setNombre(usuario.getNombre());
        entity.setEmail(usuario.getEmail());
        entity.setPasswordHash(usuario.getPasswordHash());
        entity.setRol(usuario.getRol());
        entity.setActivo(usuario.isActivo());
        return entity;
    }

    public static Locutor toDomain(LocutorEntity entity) {
        if (entity == null) return null;
        return new Locutor(
                entity.getId(),
                entity.getNombreArtistico(),
                toDomain(entity.getUsuario())
        );
    }

    public static LocutorEntity toEntity(Locutor locutor) {
        if (locutor == null) return null;
        LocutorEntity entity = new LocutorEntity();
        entity.setId(locutor.getId());
        entity.setNombreArtistico(locutor.getNombreArtistico());
        entity.setUsuario(toEntity(locutor.getUsuario()));
        return entity;
    }

    public static Programa toDomain(ProgramaEntity entity) {
        if (entity == null) return null;
        Programa programa = new Programa(
                entity.getId(),
                entity.getNombre(),
                entity.getDescripcion(),
                entity.getCategoria(),
                entity.isActivo()
        );
        programa.setLocutores(
                entity.getLocutores()
                        .stream()
                        .map(DomainMapper::toDomain)
                        .collect(Collectors.toSet())
        );
        return programa;
    }

    public static ProgramaEntity toEntity(Programa programa) {
        if (programa == null) return null;
        ProgramaEntity entity = new ProgramaEntity();
        entity.setId(programa.getId());
        entity.setNombre(programa.getNombre());
        entity.setDescripcion(programa.getDescripcion());
        entity.setCategoria(programa.getCategoria());
        entity.setActivo(programa.isActivo());
        if (programa.getLocutores() != null) {
            entity.setLocutores(
                    programa.getLocutores()
                            .stream()
                            .map(DomainMapper::toEntity)
                            .collect(Collectors.toSet())
            );
        }
        return entity;
    }

    public static Emision toDomain(EmisionEntity entity) {
        if (entity == null) return null;
        Emision emision = new Emision(
                entity.getId(),
                toDomain(entity.getPrograma()),
                entity.getDiaSemana(),
                entity.getHoraInicio(),
                entity.getHoraFin(),
                entity.getEstado()
        );
        return emision;
    }

    public static EmisionEntity toEntity(Emision emision) {
        if (emision == null) return null;
        EmisionEntity entity = new EmisionEntity();
        entity.setId(emision.getId());
        entity.setPrograma(toEntity(emision.getPrograma()));
        entity.setDiaSemana(emision.getDiaSemana());
        entity.setHoraInicio(emision.getHoraInicio());
        entity.setHoraFin(emision.getHoraFin());
        entity.setEstado(emision.getEstado());
        return entity;
    }

    public static Comentario toDomain(ComentarioEntity entity) {
        if (entity == null) return null;
        return new Comentario(
                entity.getId(),
                toDomain(entity.getEmision()),
                entity.getAutor(),
                entity.getMensaje(),
                entity.getTimestamp(),
                entity.getEstado()
        );
    }

    public static ComentarioEntity toEntity(Comentario comentario) {
        if (comentario == null) return null;
        ComentarioEntity entity = new ComentarioEntity();
        entity.setId(comentario.getId());
        entity.setEmision(toEntity(comentario.getEmision()));
        entity.setAutor(comentario.getAutor());
        entity.setMensaje(comentario.getMensaje());
        entity.setTimestamp(comentario.getTimestamp());
        entity.setEstado(comentario.getEstado());
        return entity;
    }

    public static ChatMessage toDomain(ChatMessageEntity entity) {
        if (entity == null) return null;
        return new ChatMessage(
                entity.getId(),
                toDomain(entity.getEmision()),
                entity.getAlias(),
                entity.getContenido(),
                entity.getTimestamp()
        );
    }

    public static ChatMessageEntity toEntity(ChatMessage message) {
        if (message == null) return null;
        ChatMessageEntity entity = new ChatMessageEntity();
        entity.setId(message.getId());
        entity.setEmision(toEntity(message.getEmision()));
        entity.setAlias(message.getAlias());
        entity.setContenido(message.getContenido());
        entity.setTimestamp(message.getTimestamp());
        return entity;
    }
}

