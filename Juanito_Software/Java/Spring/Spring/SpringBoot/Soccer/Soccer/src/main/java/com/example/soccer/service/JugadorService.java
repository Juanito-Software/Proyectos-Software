package com.example.soccer.service;

import com.example.soccer.Assemblers.JugadorAssembler;
import com.example.soccer.dto.JugadorDTO; // Asegúrate de tener esta importación
import com.example.soccer.model.Jugador;
import com.example.soccer.repository.JugadorRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

// Servicio para realizar operaciones básicas con jugadores usando jugadorRepository
@Service
public class JugadorService {

    private static final Logger logger = LoggerFactory.getLogger(JugadorService.class);

    @Autowired
    private JugadorRepository jugadorRepository;

    // Método para guardar una lista de jugadores a partir de datos leídos de un CSV
    public String guardarJugadores(List<String[]> jugadoresCsv) {
        logger.info("Guardando jugadores desde el CSV.");
        try {
            for (String[] jugadorData : jugadoresCsv) {
                String nombre = jugadorData[0];
                String apellido = jugadorData[1];
                LocalDate fechaNac = LocalDate.parse(jugadorData[2]);
                String posicion = jugadorData[3];

                // Verificar si ya existe un jugador con los mismos datos
                if (jugadorRepository.existsByNombreAndApellidoAndFechaNac(nombre, apellido, fechaNac)) {
                    throw new RuntimeException("El jugador " + nombre + " " + apellido + " ya existe.");
                }

                // Si no existe, guardar el jugador
                Jugador jugador = new Jugador();
                jugador.setNombre(nombre);
                jugador.setApellido(apellido);
                jugador.setFechaNac(fechaNac);
                jugador.setPosicion(posicion);
                jugadorRepository.save(jugador);
            }
            logger.info("Jugadores guardados exitosamente.");
            return "Jugadores guardados exitosamente.";
        } catch (Exception e) {
            logger.error("Error al guardar jugadores: ", e);
            return "Error al guardar los jugadores: " + e.getMessage();
        }
    }
    
    // Metodo para encontrar un jugador por su ID
    public Jugador findByIdJugador(Long id) {
        logger.info("Este es un mensaje informativo de prueba.");
        Optional<Jugador> jugadorOpt = jugadorRepository.findById(id);
        return jugadorOpt.orElse(null); // Retorna null si no se encuentra
    }
 
    // Método para encontrar un jugadorDTO por su ID
    public JugadorDTO findById(Long id) {
        logger.info("Buscando jugador con ID: " + id);
        Optional<Jugador> jugadorOpt = jugadorRepository.findById(id);
        if (jugadorOpt.isPresent()) {
            Jugador jugador = jugadorOpt.get();
            // Convertir a JugadorDTO usando jugadorAssembler
            return JugadorAssembler.jugadorToDTO(jugador);

        }else{
            logger.warn("No se encontró el jugador con ID: " + id);
            return null; 
        }
    }

    // Método para mostrar todos los jugadores
    public List<JugadorDTO> findAll() {
        logger.info("Obteniendo lista de todos los jugadores.");
        List<Jugador> jugadores = jugadorRepository.findAll();
        return jugadores.stream()
                .map(JugadorAssembler::jugadorToDTO) // Usando el ensamblador
                .collect(Collectors.toList());
    }

    // Método para actualizar un jugador por su ID
    public JugadorDTO updateJugador(JugadorDTO jugadorDto) {
        logger.info("Actualizando jugador con ID: " + jugadorDto.getId());
        Optional<Jugador> existingJugadorOpt = jugadorRepository.findById(jugadorDto.getId());
        if (existingJugadorOpt.isPresent()) {
            Jugador existingJugador = existingJugadorOpt.get();
            // Convertir el DTO a entidad usando el ensamblador
            Jugador jugador = JugadorAssembler.dtoToJugador(jugadorDto);
            // Actualiza las propiedades del jugador existente
            existingJugador.setNombre(jugador.getNombre());
            existingJugador.setApellido(jugador.getApellido());
            existingJugador.setFechaNac(jugador.getFechaNac());
            existingJugador.setPosicion(jugador.getPosicion());
            // Agrega más actualizaciones según sea necesario

            // Verificar si ya existe un jugador con los mismos datos
            if (jugadorRepository.existsByNombreAndApellidoAndFechaNac(jugador.getNombre(), jugador.getApellido(), jugador.getFechaNac())) {
                throw new RuntimeException("El jugador " + jugador.getNombre() + " " + jugador.getApellido() + " ya existe.");
            }else{
                jugadorRepository.save(existingJugador);
                logger.info("Jugador con ID: " + jugadorDto.getId() + " actualizado correctamente");
                return JugadorAssembler.jugadorToDTO(existingJugador); // Devuelve el DTO actualizado
            }
        } else {
            logger.error("Jugador no encontrado con ID: " + jugadorDto.getId());
            System.out.println("Jugador no encontrado con ID: " + jugadorDto.getId());
            return null;
        }
    }

    // Método para eliminar un jugador por su ID
    public void deleteJugador(Long id) {
        logger.info("Eliminando jugador con ID: " + id);
        Optional<Jugador> existingJugadorOpt = jugadorRepository.findById(id);
        if (existingJugadorOpt.isPresent()) {
            jugadorRepository.delete(existingJugadorOpt.get());
            logger.info("Jugador con ID " + id + " eliminado correctamente.");
        } else {
            logger.error("Jugador no encontrado con ID: " + id);
        }
    }


}

