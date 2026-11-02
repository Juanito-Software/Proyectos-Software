package com.example.BatchProcessor.service;

import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

/**
 * Procesador de paso: deja pasar cada elemento sin cambios.
 *
 * <p>Es el único procesador del proyecto y sirve para todas las rutas, porque
 * los lectores ya entregan la entidad final (el de API la deserializa
 * directamente en la clase configurada). Solo imprime cada elemento por la
 * salida estándar para poder seguir el job.
 *
 * <p>Es el sitio donde añadir transformaciones o validaciones de negocio. Si
 * {@code process} devolviera {@code null}, Spring Batch descartaría ese
 * elemento y no llegaría al escritor.
 *
 * @param <T> tipo de la entidad
 */
@Component
public class GenericProcessor<T> implements ItemProcessor<T, T> {

    /**
     * @param item elemento leído
     * @return el mismo elemento, sin modificar
     */
    @Override
    public T process(T item) {
        // Modifica o valida el dato si es necesario
        System.out.println(item.toString());

        return item;
    }
}

