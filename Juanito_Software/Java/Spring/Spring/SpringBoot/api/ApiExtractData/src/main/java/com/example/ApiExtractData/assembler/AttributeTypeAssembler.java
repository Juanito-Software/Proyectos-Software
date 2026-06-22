package com.example.ApiExtractData.assembler;

import com.example.ApiExtractData.dto.AttributeTypeDTO;
import com.example.ApiExtractData.model.Attribute;
import com.example.ApiExtractData.model.AttributeType;
import com.example.ApiExtractData.model.AttributeTypeValue;
import com.example.ApiExtractData.repository.AttributeRepository;
import com.example.ApiExtractData.repository.AttributeTypeRepository;
import com.example.ApiExtractData.repository.AttributeTypeValueRepository;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Component
public class AttributeTypeAssembler {

    private final AttributeRepository attributeRepository;
    private final AttributeTypeRepository attributeTypeRepository;
    private final AttributeTypeValueRepository attributeTypeValueRepository;

    public AttributeTypeAssembler(AttributeRepository attributeRepository, AttributeTypeRepository attributeTypeRepository, AttributeTypeValueRepository attributeTypeValueRepository) {
        this.attributeRepository = attributeRepository;
        this.attributeTypeRepository = attributeTypeRepository;
        this.attributeTypeValueRepository = attributeTypeValueRepository;
    }

    // Metodo para convertir una entidad AttributeType a AttributeTypeDTO
    public AttributeTypeDTO attributeTypeToDTO(AttributeType attributeType) {
        AttributeTypeDTO attributeTypeDto = new AttributeTypeDTO();// creamos una instancia del DTO AttributeTypeDTO
        // Mapeo de campos básicos al DTO
        attributeTypeDto.setEnumDescription(attributeType.getEnumDescription());
        attributeTypeDto.setIsEnum(attributeType.getIsEnum());
        attributeTypeDto.setIsList(attributeType.getIsList());
        attributeTypeDto.setType(attributeType.getType());



        return attributeTypeDto;
    }

    // Metodo para convertir un AttributeTypeDTO a la entidad AttributeType
    public AttributeType attributeTypeToEntity(AttributeTypeDTO attributeTypeDto) {


        // Si no se encuentra, crear un attributeType predeterminado
        AttributeType attributeType = new AttributeType();// creamos una instancia de la entidad AttributeType

        // Mapeo de campos básicos a la entidad
        attributeType.setEnumDescription(attributeTypeDto.getEnumDescription());
        attributeType.setIsEnum(attributeTypeDto.getIsEnum());
        attributeType.setIsList(attributeTypeDto.getIsList());
        attributeType.setType(attributeTypeDto.getType());



        return attributeType; // devolvemos el nuevo attributeType con datos por defecto
    }
}
