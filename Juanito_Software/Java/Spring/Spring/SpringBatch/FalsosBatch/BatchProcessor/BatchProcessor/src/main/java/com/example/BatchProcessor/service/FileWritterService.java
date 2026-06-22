package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Empleo;
import com.example.BatchProcessor.model.Persona;
import com.example.BatchProcessor.repository.EmpleoRepository;
import com.example.BatchProcessor.repository.PersonaRepository;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class FileWritterService {

    private final EmpleoRepository empleoRepository;
    private final PersonaRepository personaRepository;

    public FileWritterService(EmpleoRepository empleoRepository, PersonaRepository personaRepository) {
        this.empleoRepository = empleoRepository;
        this.personaRepository = personaRepository;
    }

    public void procesarDatosYGuardar(List<String[]> registros) {
        Map<String, Empleo> mapaEmpleos = new HashMap<>();  // Para evitar duplicados

        for (String[] campos : registros) {
            String nombrePersona = campos[0];
            String apellidoPersona = campos[1];
            String nombreEmpleo = campos[2];

            // Validación básica
            if (nombrePersona == null || apellidoPersona == null || nombreEmpleo == null) {
                continue;  // Ignorar registros inválidos
            }

            // Obtener o crear empleo
            Empleo empleo = mapaEmpleos.get(nombreEmpleo);
            if (empleo == null) {
                empleo = empleoRepository.findByNombreEmpleo(nombreEmpleo);
                if (empleo == null) {
                    empleo = new Empleo();
                    empleo.setNombreEmpleo(nombreEmpleo);
                    empleo = empleoRepository.save(empleo);
                }
                mapaEmpleos.put(nombreEmpleo, empleo);
            }

            // Crear persona y asociar empleo
            Persona persona = new Persona();
            persona.setNombre(nombrePersona);
            persona.setApellido(apellidoPersona);
            persona.setEmpleo(empleo);
            personaRepository.save(persona);
        }
    }
}
