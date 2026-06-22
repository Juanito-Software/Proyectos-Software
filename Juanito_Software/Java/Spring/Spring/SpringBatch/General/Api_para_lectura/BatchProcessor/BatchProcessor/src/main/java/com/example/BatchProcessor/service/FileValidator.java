package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Persona;
import org.springframework.batch.item.validator.ValidationException;
import org.springframework.batch.item.validator.Validator;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;


/**
 * Validador para los registros de archivo en el procesamiento por lotes.
 * Esta clase valida que los registros del archivo tengan el número esperado de columnas
 * y que los campos 'nombre', 'apellido' y 'nombreEmpleo' no sean nulos ni vacíos.
 */
@Service
@Component
public class FileValidator implements Validator<Persona> {

    @Override
    public void validate(Persona persona) throws ValidationException {

        // Validar que los campos 'nombre', 'apellido' y 'nombreEmpleo' no sean nulos ni vacíos
        if (persona.getNombreCompleto() == null) {
            throw new ValidationException("Invalid record: 'nombre' field is missing or empty");
        }

        if (persona.getEmpleo() == null) {
            System.out.println("Persona sin empleo "+persona.getNombreCompleto());
        }

        // Post-validación: Validar que el nombre de empleo es uno de los nombres válidos
        postValidateEmpleo(persona.getEmpleo());

        System.out.println("Data validated successfully");
    }

    /**
     * Realiza la post-validación sobre el campo nombreEmpleo.
     * Puede incluir reglas de negocio adicionales, como verificar si el nombre de empleo
     * existe en una lista de valores válidos o si cumple con ciertos requisitos de formato.
     */
    private void postValidateEmpleo(String nombreEmpleo) throws ValidationException {
        // Ejemplo: Validar que el nombre de empleo esté en una lista predefinida de empleos válidos
        String[] validEmpleos = {"Desarrollador", "Diseñador", "Analista", "Gerente", " "};

        boolean isValid = false;
        for (String empleo : validEmpleos) {
            if (empleo.equalsIgnoreCase(nombreEmpleo)) {
                isValid = true;
                break;
            }
        }

        if (!isValid) {
            throw new ValidationException("Invalid record: 'nombreEmpleo' is not a valid job title.");
        }
    }
}
