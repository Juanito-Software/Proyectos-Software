package com.example.soccer.service;

import com.example.soccer.Assemblers.ParticipacionAssembler;
import com.example.soccer.dto.ParticipacionDTO;

import com.example.soccer.dto.EquipoDTO;
import com.example.soccer.dto.JugadorDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.model.Jugador;
import com.example.soccer.model.Participacion;
import com.example.soccer.repository.ParticipacionRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

// Servicio para realizar operaciones basicas con participaciones usando participacionRepository
@Service
public class ParticipacionService {

    private static final Logger logger = LoggerFactory.getLogger(ParticipacionService.class);

    @Autowired
    private ParticipacionRepository participacionRepository;

    @Autowired
    private JugadorService jugadorService;

    @Autowired
    private EquipoService equipoService;

    // Método para guardar participaciones desde un CSV
    public void guardarParticipaciones(List<String[]> participacionesCsv) {
        logger.info("Guardando participaciones desde CSV.");
        List<Participacion> participaciones = new ArrayList<>();

        for (String[] data : participacionesCsv) {
            Participacion participacion = new Participacion();
            try {
                // Validar que hay suficientes datos
                if (data.length < 5 || data[0] == null || data[0].trim().isEmpty() || data[1] == null || data[1].trim().isEmpty() || data[2] == null || data[2].trim().isEmpty() || data[3] == null || data[3].trim().isEmpty() || data[4] == null || data[4].trim().isEmpty()) {
                    throw new RuntimeException("Datos insuficientes en la línea CSV: " + Arrays.toString(data));
                }

                // Buscar jugador y equipo por ID desde el CSV
                Jugador jugador = jugadorService.findByIdJugador(Long.parseLong(data[0]));
                Equipo equipo = equipoService.findByIdEquipo(Long.parseLong(data[1]));

                if (jugador != null && equipo != null) {
                    participacion.setJugador(jugador);
                    participacion.setEquipo(equipo);
                } else {
                    logger.info("Jugador o equipo no encontrado.");
                    throw new RuntimeException("Jugador o equipo no encontrado para IDs: " + data[0] + ", " + data[1]);
                }

                LocalDate fechaInicio = LocalDate.parse(data[2]);
                LocalDate fechaFin = LocalDate.parse(data[3]);
                int dorsal = Integer.parseInt(data[4]);

                // Verificar que el dorsal no esté repetido en el mismo equipo y que las fechas no se solapen
                if (participacionRepository.existsByEquipoAndDorsalAndFechas(equipo, dorsal, fechaInicio, fechaFin)) {
                    logger.error("El dorsal " + dorsal + " ya está asignado en el equipo " + equipo.getNombre() + " y se solapa en el tiempo");
                    throw new RuntimeException("El dorsal " + dorsal + " ya está asignado en el equipo " + equipo.getNombre() + " y se solapa en el tiempo");
                }else{
                    participacion.setFechaInicio(fechaInicio);
                    participacion.setFechaFin(fechaFin);
                    participacion.setDorsal(dorsal);

                    participaciones.add(participacion);
                }
            } catch (NumberFormatException | DateTimeParseException e) {
                logger.error("Error al parsear el ID del jugador o equipo: {}", e.getMessage());
                throw new RuntimeException("Error al parsear el ID del jugador o equipo: " + data[0] + ", " + data[1]);
            }
        }



        // Guardar todas las participaciones en la base de datos
        for (Participacion participacion : participaciones) {
            participacionRepository.save(participacion);
        }

        logger.info("Participaciones guardadas correctamente.");
    }

    // Método para encontrar una participación por su ID
    public ParticipacionDTO findById(Long id) {
        logger.info("Buscando participación con ID: {}", id);
        Optional<Participacion> participacionOpt = participacionRepository.findById(id);
        return participacionOpt.map(ParticipacionAssembler::participacionToDTO).orElse(null);
    }


    // Método para mostrar todas las participaciones
    public List<ParticipacionDTO> findAll() {
        logger.info("Obteniendo lista de todas las participaciones.");
        return participacionRepository.findAll().stream()
                .map(ParticipacionAssembler::participacionToDTO)
                .collect(Collectors.toList());
    }

    // Método para actualizar una participación por su ID
    public Optional<ParticipacionDTO> updateParticipacion(ParticipacionDTO participacionDTO) {
        logger.info("Actualizando participación con ID: {}", participacionDTO.getId());

        return participacionRepository.findById(participacionDTO.getId())
                .map(existingParticipacion -> {

                    // Comprobar si la participación ya ha comenzado
                    if (existingParticipacion.getFechaInicio().isBefore(LocalDate.now()) || existingParticipacion.getFechaInicio().isEqual(LocalDate.now())) {
                        existingParticipacion.setFechaFin(participacionDTO.getFechaFin());
                        throw new RuntimeException("No se pueden actualizar los datos de una participación que ya ha comenzado. Solo se podra aumentar la fechaFin");
                    }else{
                        existingParticipacion.setJugador(jugadorService.findByIdJugador(participacionDTO.getJugadorId()));
                        existingParticipacion.setEquipo(equipoService.findByIdEquipo(participacionDTO.getEquipoId()));
                        existingParticipacion.setFechaInicio(participacionDTO.getFechaInicio());
                        existingParticipacion.setFechaFin(participacionDTO.getFechaFin());
                        existingParticipacion.setDorsal(participacionDTO.getDorsal());

                        participacionRepository.save(existingParticipacion);
                        return ParticipacionAssembler.participacionToDTO(existingParticipacion);
                    }

                });
    }


    // Método para eliminar una participacion por su ID
    public void deleteParticipacion(Long id) {
        logger.info("Eliminando participacion con ID: " + id);
        Optional<Participacion> existingParticipacionOpt = participacionRepository.findById(id);
        if (existingParticipacionOpt.isPresent()) {
            Participacion existingParticipacion = existingParticipacionOpt.get();

            // Comprobar si la participación ya ha comenzado
            if (existingParticipacion.getFechaInicio().isBefore(LocalDate.now()) || existingParticipacion.getFechaInicio().isEqual(LocalDate.now())) {
                // En lugar de lanzar excepción, marcar como inactiva
                logger.info("La participación ya ha comenzado, marcándola como inactiva.");
                existingParticipacion.setActivo(false);
                participacionRepository.save(existingParticipacion);
            } else {
                // Si no ha comenzado, eliminar la participación
                participacionRepository.delete(existingParticipacion);
                logger.info("Participación con ID " + id + " eliminada correctamente.");
            }
        } else {
            logger.error("Jugador no encontrado con ID: " + id);
            throw new RuntimeException("Participación no encontrada con ID: " + id);
        }
    }

}


