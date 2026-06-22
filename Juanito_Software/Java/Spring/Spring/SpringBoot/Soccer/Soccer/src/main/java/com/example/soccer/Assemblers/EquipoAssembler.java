package com.example.soccer.Assemblers;

import com.example.soccer.dto.EquipoDTO;
import com.example.soccer.dto.JugadorDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.model.Jugador;

public class EquipoAssembler {

    public static EquipoDTO equipoToDTO (Equipo equipo) {
        EquipoDTO equipoDTO= new EquipoDTO();
        equipoDTO.setId(equipo.getId());
        equipoDTO.setNombre(equipo.getNombre());
        equipoDTO.setCiudad(equipo.getCiudad());
        equipoDTO.setFechaFundacion(equipo.getFechaFundacion());
        return equipoDTO;
    }

    public static Equipo dtoToEquipo(EquipoDTO equipoDTO) {
        Equipo equipo = new Equipo();
        equipo.setId(equipoDTO.getId());
        equipo.setNombre(equipoDTO.getNombre());
        equipo.setCiudad(equipoDTO.getCiudad());
        equipo.setFechaFundacion(equipoDTO.getFechaFundacion());
        return equipo;
    }

}
