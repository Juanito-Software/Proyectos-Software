package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Persona;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

import java.util.Map;

// Esta clase se utiliza para procesar los datos del Map<String, String> y convertirlos en un objeto Persona.
@Component
public class PersonaItemProcessor implements ItemProcessor<Map<String, Object>, Persona> {

    @Override
    public Persona process(Map<String, Object> personaMap) throws Exception {
        System.out.println("Procesando persona: " + personaMap);
        System.out.println("Claves en el mapa: " + personaMap.keySet());

        // Verificar el tipo del valor de personaId en el mapa
        Object personaIdObj = personaMap.get("personaId");

        // Convertir Map<String, Object> a un objeto Persona
        Long personaId = null;
        personaId = ((Integer) personaIdObj).longValue();
        String nombreCompleto = (String) personaMap.get("nombreCompleto");  // Obtener nombreCompleto como String
        String empleo = (String) personaMap.get("empleo");  // Obtener empleo como String

        // Crear la instancia de Persona
        Persona persona = new Persona();
        if (personaId != null) {
            persona.setPersonaId(personaId);  // Convertir el ID de String a Long
        }
        persona.setNombreCompleto(nombreCompleto);
        persona.setEmpleo(empleo);

        return persona;
    }
}
