package com.example.BatchProcessor.service;

import com.example.BatchProcessor.model.Empleo;
import com.example.BatchProcessor.model.FileRecord;
import com.example.BatchProcessor.model.Persona;
import io.micrometer.core.instrument.config.validate.ValidationException;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;


/**
 * Procesador de registros de archivos CSV.
 * Esta clase procesa los registros leídos de los archivos, convirtiéndolos en objetos Persona que se almacenarán
 * en la base de datos. Utiliza la información del empleo para asociarlo a la persona.
 */
@Component
public class RecordProcessor implements ItemProcessor<FileRecord, Persona> {

    private final FileValidator fileValidator;

    public RecordProcessor(FileValidator fileValidator) {
        this.fileValidator = fileValidator;
    }

    @Override
    public Persona process(FileRecord record) {

        // Validamos el registro antes de procesarlo
        try {
            fileValidator.validate(record);  // Llamamos al validador
        } catch (ValidationException e) {
            // Manejo de la validación fallida, por ejemplo, podrías registrar un error o simplemente ignorar el registro
            System.err.println("Validation failed for record: " + e.getMessage());
            return null;  // O puedes decidir omitir el registro
        }

        Persona persona = new Persona();
        persona.setNombreCompleto(record.getNombre() + " " + record.getApellido());

        // Asignar Empleo basado en el nombre del empleo
        Empleo empleo = new Empleo(record.getNombreEmpleo());
        persona.setEmpleo(empleo);

        return persona;
    }
}
