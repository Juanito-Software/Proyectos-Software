package com.example.BatchProcessor.writer;

import com.example.BatchProcessor.model.Empleo;
import com.example.BatchProcessor.model.Persona;
import com.example.BatchProcessor.repository.EmpleoRepository;
import com.example.BatchProcessor.repository.PersonaRepository;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.stereotype.Component;

import java.util.List;


/**
 * Escritor de base de datos para almacenar objetos Persona y Empleo.
 * Esta clase guarda las personas y los empleos relacionados en la base de datos,
 * asegurando que los empleos no se guarden repetidos.
 */
@Component
public class DatabaseWriter implements ItemWriter<Persona> {  // Renombrado a DatabaseWriter

    private final PersonaRepository personaRepository;
    private final EmpleoRepository empleoRepository;

    public DatabaseWriter(PersonaRepository personaRepository, EmpleoRepository empleoRepository) {
        this.personaRepository = personaRepository;
        this.empleoRepository = empleoRepository;
    }

    @Override
    public void write(Chunk<? extends Persona> chunk) throws Exception {
        // Iterar sobre los elementos del chunk y guardarlos
        List<? extends Persona> personas = chunk.getItems();

        // Guardar los empleos primero (evitar duplicados)   // procesamiento secuencial (en serie)
        List<Empleo> empleosSinId = personas.stream()
                .map(Persona::getEmpleo)
                .filter(empleo -> empleo != null && empleo.getEmpleoId() == null)
                .distinct() // Evita guardar empleos repetidos
                .toList();
        empleoRepository.saveAll(empleosSinId);

        // Guardar todas las personas en una sola operación
        personaRepository.saveAll(personas);
    }
}
