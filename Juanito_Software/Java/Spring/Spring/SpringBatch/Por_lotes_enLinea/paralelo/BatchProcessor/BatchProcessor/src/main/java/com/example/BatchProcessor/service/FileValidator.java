package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Empleo;
import com.example.BatchProcessor.model.FileRecord;
import com.example.BatchProcessor.model.Persona;
import org.springframework.batch.item.validator.ValidationException;
import org.springframework.batch.item.validator.Validator;
import org.springframework.stereotype.Component;


/**
 * Validador para los registros de archivo en el procesamiento por lotes.
 * Esta clase valida que los registros del archivo tengan el número esperado de columnas
 * y que los campos 'nombre', 'apellido' y 'nombreEmpleo' no sean nulos ni vacíos.
 */
@Component
public class FileValidator implements Validator<FileRecord> {
    private static final int EXPECTED_COLUMN_COUNT = 3; // Cambiar según las columnas esperadas

    @Override
    public void validate(FileRecord record) throws ValidationException {
        // Validar la estructura del registro
        String[] columns = record.getRawData().split(","); // Asumimos que FileRecord tiene un metodo getRawData()
        if (columns.length != EXPECTED_COLUMN_COUNT) {
            throw new ValidationException("Invalid record: incorrect number of columns. Expected "
                    + EXPECTED_COLUMN_COUNT + ", but found " + columns.length);
        }

        // Validar que los campos 'nombre', 'apellido' y 'nombreEmpleo' no sean nulos ni vacíos
        if (record.getNombre() == null || record.getNombre().isBlank()) {
            throw new ValidationException("Invalid record: 'nombre' field is missing or empty");
        }
        if (record.getApellido() == null || record.getApellido().isBlank()) {
            throw new ValidationException("Invalid record: 'apellido' field is missing or empty");
        }
        if (record.getNombreEmpleo() == null || record.getNombreEmpleo().isBlank()) {
            throw new ValidationException("Invalid record: 'nombreEmpleo' field is missing or empty");
        }

        // Post-validación: Validar que el nombre de empleo es uno de los nombres válidos
        postValidateEmpleo(record.getNombreEmpleo());

        System.out.println("Data validated successfully");
    }

    /**
     * Realiza la post-validación sobre el campo nombreEmpleo.
     * Puede incluir reglas de negocio adicionales, como verificar si el nombre de empleo
     * existe en una lista de valores válidos o si cumple con ciertos requisitos de formato.
     */
    private void postValidateEmpleo(String nombreEmpleo) throws ValidationException {
        // Ejemplo: Validar que el nombre de empleo esté en una lista predefinida de empleos válidos
        String[] validEmpleos = {"Desarrollador", "Diseñador", "Analista", "Gerente"};

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
