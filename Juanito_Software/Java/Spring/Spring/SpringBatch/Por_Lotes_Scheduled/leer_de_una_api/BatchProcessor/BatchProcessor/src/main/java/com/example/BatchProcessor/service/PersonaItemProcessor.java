package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Empleo;
import com.example.BatchProcessor.model.Persona;
import com.example.BatchProcessor.repository.EmpleoRepository;
import com.example.BatchProcessor.repository.PersonaRepository;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@Component
public class PersonaItemProcessor implements ItemProcessor<Persona, Persona> {

    private final EmpleoRepository empleoRepository;

    public PersonaItemProcessor(EmpleoRepository empleoRepository) {
        this.empleoRepository = empleoRepository;
    }

    @Override
    public Persona process(Persona persona) throws Exception {
        if (persona.getEmpleo() != null) {
            Empleo empleo = persona.getEmpleo();
            // Buscar empleo por nombre o crearlo si no existe
            empleo = empleoRepository.findByNombreEmpleo(empleo.getNombreEmpleo())
                    .orElseGet(() -> empleoRepository.saveAndFlush(persona.getEmpleo()));
            // Asignar el empleo persistido a la persona
            persona.setEmpleo(empleo);
        }
        return persona;
    }
}
