package com.example.BatchProcessor.service;

import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;

@Component
public class GenericProcessor<T> implements ItemProcessor<T, T> {
    @Override
    public T process(T item) {
        // Modifica o valida el dato si es necesario
        return item;
    }
}

