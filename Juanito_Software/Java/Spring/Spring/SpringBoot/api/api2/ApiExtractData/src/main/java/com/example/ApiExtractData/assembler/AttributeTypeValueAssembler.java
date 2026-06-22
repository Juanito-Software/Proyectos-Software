package com.example.ApiExtractData.assembler;

import com.example.ApiExtractData.dto.AttributeTypeValueDTO;
import com.example.ApiExtractData.model.Attribute;
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
        dto.setId(attributeTypeValue.getId());
        dto.setDescription(attributeTypeValue.getDescription());
        dto.setValue(attributeTypeValue.getValue());

        if (attributeTypeValue.getAttributeType() != null) {
            dto.setAttributeTypeId(attributeTypeValue.getAttributeType().getId());
        }

        return dto;
    }

    // Metodo para convertir AttributeTypeValueDTO a AttributeTypeValue
    public AttributeTypeValue attributeTypeValueToEntity(AttributeTypeValueDTO attributeTypeValueDto) {

        if (attributeTypeValueDto.getId() != null) {// buscamos el attributeTypeValue por su id
            Optional<AttributeTypeValue> existingAttribute = attributeTypeValueRepository.findById(attributeTypeValueDto.getId());
            if (existingAttribute.isPresent()) {
                System.out.println("attributetypevalue existe");
                AttributeTypeValue attributeTypeValue = existingAttribute.get(); // Retornar el attributeTypeValue existente
                attributeTypeValue.setDescription(attributeTypeValueDto.getDescription());
                attributeTypeValue.setValue(attributeTypeValueDto.getValue());

                return attributeTypeValue;
            }
        }
        System.out.println("attributetypevalue no existe");
        // Si no se encuentra, crear un attributeTypeValue predeterminado
        AttributeTypeValue attributeTypeValue = new AttributeTypeValue();
        attributeTypeValue.setId(attributeTypeValueDto.getId());
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
                        newattributeTypeExample.setAttributes(null);
                        newattributeTypeExample.setAttributeTypeValues(null);
                        return attributeTypeRepository.save(newattributeTypeExample);// devolvemos el nuevo attributeType con datos por defecto
                    });
            attributeTypeValue.setAttributeType(attributeType); //añadimos al attribute el attributeType
        }
        return attributeTypeValue;// devolvemos el nuevo config con datos por defecto
    }
}
