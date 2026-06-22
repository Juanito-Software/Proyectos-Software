package com.example.soccer.Assemblers;

import com.example.soccer.dto.ParticipacionDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.model.Jugador;
import com.example.soccer.model.Participacion;

public class ParticipacionAssembler {

    // Convierte una entidad Participacion a ParticipacionDTO
    public static ParticipacionDTO participacionToDTO(Participacion participacion) {
        ParticipacionDTO dto = new ParticipacionDTO();
        dto.setId(participacion.getId());
        dto.setJugadorId(participacion.getJugador().getId());  // Asumiendo relación Jugador
        dto.setEquipoId(participacion.getEquipo().getId());    // Asumiendo relación Equipo
        dto.setFechaInicio(participacion.getFechaInicio());
        dto.setFechaFin(participacion.getFechaFin());
        dto.setDorsal(participacion.getDorsal());
        return dto;
    }

    // Convierte un ParticipacionDTO a una entidad Participacion
    public static Participacion dtoToParticipacion(ParticipacionDTO dto, Jugador jugador, Equipo equipo) {
        Participacion participacion = new Participacion();
        participacion.setId(dto.getId());
        participacion.setJugador(jugador);  // Jugador obtenido por servicio
        participacion.setEquipo(equipo);    // Equipo obtenido por servicio
        participacion.setFechaInicio(dto.getFechaInicio());
        participacion.setFechaFin(dto.getFechaFin());
        participacion.setDorsal(dto.getDorsal());
        return participacion;
    }
}
