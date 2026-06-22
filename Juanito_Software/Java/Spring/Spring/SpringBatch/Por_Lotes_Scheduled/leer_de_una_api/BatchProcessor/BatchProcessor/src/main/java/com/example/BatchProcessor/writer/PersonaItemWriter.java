package com.example.BatchProcessor.writer;

import com.example.BatchProcessor.model.Empleo;
import com.example.BatchProcessor.model.Persona;
import com.example.BatchProcessor.repository.EmpleoRepository;
import com.example.BatchProcessor.repository.PersonaRepository;
import jakarta.persistence.EntityManager;
import jakarta.transaction.Transactional;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;


/**
 * Escritor de base de datos para almacenar objetos Persona y Empleo.
 * Esta clase guarda las personas y los empleos relacionados en la base de datos,
 * asegurando que los empleos no se guarden repetidos.
 */
@Component
public class PersonaItemWriter implements ItemWriter<Persona> {

    private final PersonaRepository personaRepository;

    public PersonaItemWriter(PersonaRepository personaRepository) {
        this.personaRepository = personaRepository;
    }

    @Override
    public void write(Chunk<? extends Persona> chunk) throws Exception {
        // Convertir el Chunk a una lista
        List<? extends Persona> items = chunk.getItems();

        // Filtrar las personas que no existen en la base de datos
        List<Persona> personasNuevas = items.stream()
                .filter(persona -> !personaRepository.existsByNombreCompleto(persona.getNombreCompleto()))
                .collect(Collectors.toList());

        // Guardar todas las personas nuevas en una sola operación
        if (!personasNuevas.isEmpty()) {
            personaRepository.saveAll(personasNuevas);
        }
    }
}
