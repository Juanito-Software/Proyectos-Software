package com.example.ApiExtractData.repository;

import com.example.ApiExtractData.model.Attribute;
import com.example.ApiExtractData.model.Config;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AttributeRepository extends JpaRepository<Attribute, Long> {

}

