package com.example.BatchProcessor.repository;

import com.example.BatchProcessor.model.GenericEntity;
import com.example.BatchProcessor.model.MyEntity;
import org.springframework.stereotype.Repository;

@Repository
public interface MyEntityRepository extends GenericRepository<MyEntity, Long> {
}


