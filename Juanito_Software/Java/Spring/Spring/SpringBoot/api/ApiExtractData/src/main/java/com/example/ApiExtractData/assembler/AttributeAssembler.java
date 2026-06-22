package com.example.ApiExtractData.assembler;

import com.example.ApiExtractData.dto.AttributeDTO;
import com.example.ApiExtractData.model.Attribute;
import com.example.ApiExtractData.model.AttributeType;
import com.example.ApiExtractData.model.Config;
import com.example.ApiExtractData.repository.AttributeRepository;
import com.example.ApiExtractData.repository.AttributeTypeRepository;
import com.example.ApiExtractData.repository.ConfigRepository;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
public class AttributeAssembler {

    private final ConfigRepository configRepository;
    private final AttributeTypeRepository attributeTypeRepository;
    private final AttributeRepository attributeRepository;

    public AttributeAssembler(ConfigRepository configRepository, AttributeTypeRepository attributeTypeRepository, AttributeRepository attributeRepository) {
        this.configRepository = configRepository;
        this.attributeTypeRepository = attributeTypeRepository;
        this.attributeRepository = attributeRepository;
    }

    // Metodo para convertir una entidad Attribute a AttributeDTO
    public AttributeDTO attributeToDTO(Attribute attribute) {
        AttributeDTO attributeDTO = new AttributeDTO();// creamos una instancia del DTO AttributeDTO
        // Mapeo de campos básicos al DTO
        attributeDTO.setName(attribute.getName());
        return attributeDTO;
    }

    // Convierte de DTO a Entity
    public Attribute attributeToEntity(AttributeDTO attributeDto) {

        // creamos un objeto attribute predeterminado
        Attribute attribute=new Attribute();

        // Mapeo de campos básicos
        attribute.setName(attributeDto.getName());



        // Guardar la entidad (ya sea una existente o una nueva)
        return attributeRepository.save(attribute);
    }
}
