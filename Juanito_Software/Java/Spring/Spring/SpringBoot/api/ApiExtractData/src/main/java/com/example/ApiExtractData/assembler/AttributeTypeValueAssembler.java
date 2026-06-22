package com.example.ApiExtractData.assembler;

import com.example.ApiExtractData.dto.AttributeTypeValueDTO;
import com.example.ApiExtractData.model.AttributeType;
import com.example.ApiExtractData.model.AttributeTypeValue;
import com.example.ApiExtractData.repository.AttributeTypeRepository;
import com.example.ApiExtractData.repository.AttributeTypeValueRepository;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
public class AttributeTypeValueAssembler {

    private final AttributeTypeValueRepository attributeTypeValueRepository;
    private final AttributeTypeRepository attributeTypeRepository;

    public AttributeTypeValueAssembler(AttributeTypeValueRepository attributeTypeValueRepository, AttributeTypeRepository attributeTypeRepository) {
        this.attributeTypeValueRepository = attributeTypeValueRepository;
        this.attributeTypeRepository = attributeTypeRepository;
    }

    // Metodo para convertir AttributeTypeValue a AttributeTypeValueDTO
    public AttributeTypeValueDTO attributeTypeValueToDTO(AttributeTypeValue attributeTypeValue) {
        AttributeTypeValueDTO dto = new AttributeTypeValueDTO();
        dto.setDescription(attributeTypeValue.getDescription());
        dto.setValue(attributeTypeValue.getValue());

        if (attributeTypeValue.getAttributeType() != null) {
            dto.setAttributeTypeId(attributeTypeValue.getAttributeType().getId());
        }

        return dto;
    }

    // Metodo para convertir AttributeTypeValueDTO a AttributeTypeValue
    public AttributeTypeValue attributeTypeValueToEntity(AttributeTypeValueDTO attributeTypeValueDto) {

        // Si no se encuentra, crear un attributeTypeValue predeterminado
        AttributeTypeValue attributeTypeValue = new AttributeTypeValue();
        attributeTypeValue.setDescription(attributeTypeValueDto.getDescription());
        attributeTypeValue.setValue(attributeTypeValueDto.getValue());

        // Asignar relación con AttributeType
        if (attributeTypeValueDto.getAttributeTypeId() != null) {
            AttributeType attributeType = attributeTypeRepository.findById(attributeTypeValueDto.getAttributeTypeId())// buscamos un attributeType por su id
                    .orElseGet(() -> {
                        // Si no se encuentra, crear un attributeType predeterminado
                        AttributeType newattributeTypeExample = new AttributeType();
                        newattributeTypeExample.setId(attributeTypeValueDto.getAttributeTypeId());
                        newattributeTypeExample.setEnumDescription("Example");
                        newattributeTypeExample.setIsEnum(false);
                        newattributeTypeExample.setIsList(false);
                        newattributeTypeExample.setType("prueba");

                        return attributeTypeRepository.save(newattributeTypeExample);// devolvemos el nuevo attributeType con datos por defecto
                    });
            attributeTypeValue.setAttributeType(attributeType); //añadimos al attribute el attributeType
        }
        return attributeTypeValue;// devolvemos el nuevo config con datos por defecto
    }
}
