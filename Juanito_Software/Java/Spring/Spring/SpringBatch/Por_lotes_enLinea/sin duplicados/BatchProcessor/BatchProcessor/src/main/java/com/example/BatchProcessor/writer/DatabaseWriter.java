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

import java.util.*;
import java.util.stream.Collectors;


/**
 * Escritor de base de datos para almacenar objetos Persona y Empleo.
 * Esta clase guarda las personas y los empleos relacionados en la base de datos,
 * asegurando que los empleos no se guarden repetidos.
 */
@Component
public class DatabaseWriter implements ItemWriter<Persona> {  // Renombrado a DatabaseWriter

    private final PersonaRepository personaRepository;
    private final EmpleoRepository empleoRepository;
    private EntityManager entityManager;

    public DatabaseWriter(PersonaRepository personaRepository, EmpleoRepository empleoRepository, EntityManager entityManager) {
        this.personaRepository = personaRepository;
        this.empleoRepository = empleoRepository;
        this.entityManager = entityManager;
    }

    @Transactional
    @Override
    public void write(Chunk<? extends Persona> chunk) throws Exception {
        try {
            // Obtener las personas que vienen en el chunk
            List<? extends Persona> personas = chunk.getItems();



            // Extraer los empleos de las personas, asegurándonos de no tener duplicados
            List<Empleo> empleos = personas.stream()
                    .map(Persona::getEmpleo)
                    .distinct() // Evita los duplicados de empleos
                    .collect(Collectors.toList());

            List<Empleo> empleosPersistidos = empleoRepository.saveAll(empleos);// Guardar los empleos primero, para evitar errores
            empleoRepository.flush();// Asegurarse de que los cambios se persistan en la base de datos

            // Asociar las instancias persistidas de Empleo a las personas
            personas.forEach(persona -> {
                Empleo empleoOriginal = persona.getEmpleo();
                Empleo empleoPersistido = empleosPersistidos.stream()
                        .filter(e -> e.equals(empleoOriginal)) // Usamos equals para encontrar el match
                        .findFirst()
                        .orElseThrow(() -> new IllegalStateException("No se encontró el empleo persistido"));
                persona.setEmpleo(empleoPersistido); // Actualizamos el empleo en la persona
            });




            // Aquí se realiza la comparación y actualización si el nombre de la persona ya existe en la base de datos pero el empleo cambia
            for (Persona nueva : personas) {
                // Verificar si ya existe una persona con el mismo nombre
                Optional<Persona> existenteOpt = personaRepository.findByNombreCompleto(nueva.getNombreCompleto());

                if (existenteOpt.isPresent()) {
                    Persona existente = existenteOpt.get();

                    // Si existe, actualizamos el empleo de esa persona
                    if (!existente.getEmpleo().equals(nueva.getEmpleo())) {
                        // Solo actualizamos si el empleo ha cambiado
                        existente.setEmpleo(nueva.getEmpleo());
                        System.out.println("Empleo actualizado para: " + existente.getNombreCompleto());
                        personaRepository.save(existente); // Guardar los cambios
                    }else{
                        System.out.println("Empleo no actualizado para: " + existente.getNombreCompleto()+" porque sigue teniendo el mismo empleo");
                    }
                } else {
                    // Si no se encuentra la persona, loguear el evento y continuar con la siguiente
                    System.out.println("Empleo no actualizado, persona no encontrada en la base de datos: " + nueva.getNombreCompleto());
                }
            }




            // Filtrar las personas para agregar solo las nuevas (evitar duplicados)
            List<Persona> personasNuevas = personas.stream()
                    // Evita guardar personas repetidas
                    .filter(persona -> !personaRepository.existsByNombreCompleto(persona.getNombreCompleto()))
                    .distinct()
                    .collect(Collectors.toList());
            // Guardar todas las personas en una sola operación (solo las únicas)
            personaRepository.saveAll(personasNuevas);// Guardar los empleos primero, para evitar duplicados

            // Asegurarse de que los cambios se persistan en la base de datos
            personaRepository.flush();

            // Limpiar el contexto de persistencia para liberar memoria
            entityManager.clear();

        } catch (Exception e) {
            // Loguear el error para obtener más detalles
            System.err.println("Error durante el commit del chunk: " + e.getMessage());
            throw e;  // Re-lanzar la excepción para que Spring Batch maneje el rollback
        }

        // antes guardabamos empleos y personas permitiendo duplicados

        // Iterar sobre los elementos del chunk y guardarlos
        /*List<? extends Persona> personas = chunk.getItems();

        // Guardar los empleos primero
        List<Empleo> empleosSinId = personas.stream()
                .map(Persona::getEmpleo)
                .filter(empleo -> empleo != null && empleo.getEmpleoId() == null)
                .distinct() // Evita guardar empleos repetidos
                .toList();
        empleoRepository.saveAll(empleosSinId);

        // Guardar todas las personas en una sola operación
        personaRepository.saveAll(personas);*/
    }
}
