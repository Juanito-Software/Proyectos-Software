package com.example.soccer.service;


import com.example.soccer.Assemblers.EquipoAssembler;
import com.example.soccer.dto.EquipoDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.repository.EquipoRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// Servicio para realizar operaciones basicas con equipos usando equipoRepository, utilizado en su mayoria por DataController
// El servicio tambien contiene un metodo "guardarEquipos" utilizado por CsvController
@Service // Anotación que indica que esta clase es un servicio de Spring
public class EquipoService {

    private static final Logger logger = LoggerFactory.getLogger(EquipoService.class);

    @Autowired
    private EquipoRepository equipoRepository;
    
    // Metodo para guardar una lista de equipos a partir de datos leídos de un CSV
    public void guardarEquipos(List<String[]> equiposCsv) {
        logger.info("Guardando equipos desde CSV.");
        for (String[] equipoData : equiposCsv) {
            String nombre = equipoData[0];
            String Ciudad = equipoData[1];
            LocalDate FechaFundacion = LocalDate.parse(equipoData[2]);

            // Verificar si ya existe un equipo con los mismos datos
            if (equipoRepository.existsByNombreAndCiudad(nombre, Ciudad)) {
                throw new RuntimeException("El equipo " + nombre + " " + Ciudad + " ya existe.");
            }

            Equipo equipo = new Equipo();
            equipo.setNombre(nombre);
            equipo.setCiudad(Ciudad);
            equipo.setFechaFundacion(FechaFundacion);
            equipoRepository.save(equipo);
        }
    }

        // Metodo para encontrar un equipo por su ID
    public Equipo findByIdEquipo(Long id) {
        logger.info("Este es un mensaje informativo de prueba.");
        Optional<Equipo> equipoOpt = equipoRepository.findById(id);
        return equipoOpt.orElse(null); // Retorna null si no se encuentra
    }

    public Optional<EquipoDTO> findById(Long id) {
        logger.info("Buscando equipo con ID: {}", id);
        return equipoRepository.findById(id).map(EquipoAssembler::equipoToDTO);
    }


    public List<EquipoDTO> findAll() {
        logger.info("Obteniendo lista de todos los equipos.");
        return equipoRepository.findAll().stream()
                .map(EquipoAssembler::equipoToDTO)
                .collect(Collectors.toList());
    }

    public Optional<EquipoDTO> updateEquipo(EquipoDTO equipoDTO) {
        logger.info("Actualizando equipo con ID: {}", equipoDTO.getId());
        return equipoRepository.findById(equipoDTO.getId())
                .map(existingEquipo -> {
                    Equipo equipo = EquipoAssembler.dtoToEquipo(equipoDTO); // Convertir DTO a entidad

                    // Verificar si ya existe un equipo con los mismos datos
                    if (equipoRepository.existsByNombreAndCiudad(equipo.getNombre(), equipo.getCiudad())) {
                        throw new RuntimeException("El equipo " + equipo.getNombre() + " " + equipo.getCiudad() + " ya existe.");
                    }

                    equipoRepository.save(equipo);
                    return EquipoAssembler.equipoToDTO(equipo);
                }); // Retorna un Optional
    }

    public void deleteEquipo(Long id) {
        logger.info("Eliminando equipo con ID: {}", id);
        equipoRepository.findById(id).ifPresentOrElse(equipo -> {
            equipoRepository.delete(equipo);
            logger.info("Equipo con ID {} eliminado correctamente.", id);
        }, () -> logger.error("Equipo no encontrado con ID: {}", id));
    }



}

