package com.example.soccer.Assemblers;

import com.example.soccer.dto.JugadorDTO;
import com.example.soccer.model.Jugador;

public class JugadorAssembler {

    public static JugadorDTO jugadorToDTO(Jugador jugador) {
        JugadorDTO dto = new JugadorDTO();
        dto.setId(jugador.getId());
        dto.setNombre(jugador.getNombre());
        dto.setApellido(jugador.getApellido());
        dto.setFechaNac(jugador.getFechaNac());
        dto.setPosicion(jugador.getPosicion());
        return dto;
    }

    public static Jugador dtoToJugador(JugadorDTO dto) {
        Jugador jugador = new Jugador();
        jugador.setId(dto.getId());
        jugador.setNombre(dto.getNombre());
        jugador.setApellido(dto.getApellido());
        jugador.setFechaNac(dto.getFechaNac());
        jugador.setPosicion(dto.getPosicion());
        return jugador;
    }

    // Nuevo método para convertir Jugador a JugadorDTO
    private static JugadorDTO convertToDTO(Jugador jugador) {
        return new JugadorDTO(
                jugador.getId(),
                jugador.getNombre(),
                jugador.getApellido(),
                jugador.getFechaNac(),
                jugador.getPosicion()
        );
    }

    // método para convertir JugadorDTO a Jugador
    public static Jugador convertToEntity(JugadorDTO jugadorDTO) {
        Jugador jugador = new Jugador();
        jugador.setId(jugadorDTO.getId());
        jugador.setNombre(jugadorDTO.getNombre());
        jugador.setApellido(jugadorDTO.getApellido());
        jugador.setFechaNac(jugadorDTO.getFechaNac());
        jugador.setPosicion(jugadorDTO.getPosicion());
        return jugador;
    }

}
