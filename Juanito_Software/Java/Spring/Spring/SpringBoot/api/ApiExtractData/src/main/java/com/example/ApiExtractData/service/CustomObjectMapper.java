package com.example.ApiExtractData.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

//Creamos una clase que extendemos de ObjectMapper para que los json se muestren correctamente identados al hacer consultas
public class CustomObjectMapper extends ObjectMapper {
    public CustomObjectMapper() {
        // Activa la indentación para generar JSON legible
        this.enable(SerializationFeature.INDENT_OUTPUT);
        // Registra el módulo para manejar tipos de fecha y hora de Java 8
        this.registerModule(new JavaTimeModule());
    }

    // otra opción es extender el metodo que sirve para escribir json
    /*@Override
    public String writeValueAsString(Object value) throws JsonProcessingException {
        BufferRecycler br = this._jsonFactory._getBufferRecycler();

        Object result;
        try {
            SegmentedStringWriter sw = new SegmentedStringWriter(br);
            Throwable var4 = null;

            try {
                // Create a JSON generator and enable pretty printing for better readability
                JsonGenerator generator = this.createGenerator((Writer) sw);
                generator.useDefaultPrettyPrinter();

                this._writeValueAndClose(generator, value);
                result = sw.getAndClear();
            } catch (Throwable var25) {
                result = var25;
                var4 = var25;
                throw var25;
            } finally {
                if (sw != null) {
                    if (var4 != null) {
                        try {
                            sw.close();
                        } catch (Throwable var24) {
                            var4.addSuppressed(var24);
                        }
                    } else {
                        sw.close();
                    }
                }
            }
        } catch (JsonProcessingException var27) {
            throw var27;
        } catch (IOException var28) {
            throw JsonMappingException.fromUnexpectedIOE(var28);
        } finally {
            br.releaseToPool();
        }

        return (String) result;
    }*/
}