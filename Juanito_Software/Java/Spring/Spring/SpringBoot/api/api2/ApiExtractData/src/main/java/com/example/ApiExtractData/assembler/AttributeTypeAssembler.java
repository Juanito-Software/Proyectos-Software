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
        attributeTypeDto.setId(attributeType.getId());
        attributeTypeDto.setEnumDescription(attributeType.getEnumDescription());
        attributeTypeDto.setIsEnum(attributeType.getIsEnum());
        attributeTypeDto.setIsList(attributeType.getIsList());
        attributeTypeDto.setType(attributeType.getType());

        // Mapeo de los atributos y valores a listas de IDs
        List<Long> attributeIds = attributeType.getAttributes().stream()
                .map(Attribute::getId)
                .collect(Collectors.toList());
        attributeTypeDto.setAttributeIds(attributeIds);

        List<Long> attributeTypeValueIds = attributeType.getAttributeTypeValues().stream()
                .map(AttributeTypeValue::getId)
                .collect(Collectors.toList());
        attributeTypeDto.setAttributeTypeValueIds(attributeTypeValueIds);

        return attributeTypeDto;
    }

    // Metodo para convertir un AttributeTypeDTO a la entidad AttributeType
    public AttributeType attributeTypeToEntity(AttributeTypeDTO attributeTypeDto) {

        // Si el ID no es nulo, verificar si el objeto ya existe en la base de datos
        if (attributeTypeDto.getId() != null) {
            Optional<AttributeType> existingAttributeType = attributeTypeRepository.findById(attributeTypeDto.getId());
            if (existingAttributeType.isPresent()) {
                System.out.println("AttributeType ya existe en la base de datos.");

                // Obtenemos la entidad existente y actualizamos los valores necesarios
                AttributeType attributeType = existingAttributeType.get();
                attributeType.setEnumDescription(attributeTypeDto.getEnumDescription());
                attributeType.setIsEnum(attributeTypeDto.getIsEnum());
                attributeType.setIsList(attributeTypeDto.getIsList());
                attributeType.setType(attributeTypeDto.getType());

                // Actualizar relaciones con Attribute y AttributeTypeValue
                updateAttributes(attributeType, attributeTypeDto);
                updateAttributeTypeValues(attributeType, attributeTypeDto);

                return attributeType;
            }
        }

        System.out.println("AttributeType no existe, creando una nueva instancia.");

        // Si no existe, crear una nueva instancia de AttributeType y mapear los valores del DTO
        AttributeType attributeType = new AttributeType();
        attributeType.setId(attributeTypeDto.getId());
        attributeType.setEnumDescription(attributeTypeDto.getEnumDescription());
        attributeType.setIsEnum(attributeTypeDto.getIsEnum());
        attributeType.setIsList(attributeTypeDto.getIsList());
        attributeType.setType(attributeTypeDto.getType());

        // Mapear relaciones
        updateAttributes(attributeType, attributeTypeDto);
        updateAttributeTypeValues(attributeType, attributeTypeDto);

        return attributeType;
    }

    // Metodo auxiliar para actualizar la lista de atributos
    private void updateAttributes(AttributeType attributeType, AttributeTypeDTO attributeTypeDto) {
        if (attributeTypeDto.getAttributeIds() != null) { // Solo si attributeIds no es null
            List<Attribute> attributes = attributeTypeDto.getAttributeIds()
                    .stream()
                    .map(attributeRepository::findById)
                    .filter(Optional::isPresent)
                    .map(Optional::get)
                    .collect(Collectors.toList());
            attributeType.setAttributes(attributes);
        }
    }

    // Metodo auxiliar para actualizar la lista de valores de tipo de atributo
    private void updateAttributeTypeValues(AttributeType attributeType, AttributeTypeDTO attributeTypeDto) {
        if (attributeTypeDto.getAttributeTypeValueIds() != null) {
            List<AttributeTypeValue> attributeTypeValues = attributeTypeDto.getAttributeTypeValueIds().stream()
                    .map(attributeTypeValueRepository::findById)
                    .filter(Optional::isPresent)
                    .map(Optional::get)
                    .collect(Collectors.toList());
            attributeType.setAttributeTypeValues(attributeTypeValues);
        }
    }

}
