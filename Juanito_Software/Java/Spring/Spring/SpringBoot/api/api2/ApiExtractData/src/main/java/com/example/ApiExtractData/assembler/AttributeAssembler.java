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
        attributeDTO.setId(attribute.getId());
        attributeDTO.setName(attribute.getName());
        attributeDTO.setAttributeTypeId(attribute.getAttributeType() != null ? attribute.getAttributeType().getId() : null); // Asigna el ID del AttributeType al attributeDTO. Si attributeType no es null, se obtiene su ID; de lo contrario, se asigna null.
        attributeDTO.setConfigId(attribute.getConfig() != null ? attribute.getConfig().getId() : null); // Asigna el ID del Config al configDTO. Si Config no es null, se obtiene su ID; de lo contrario, se asigna null.
        return attributeDTO;
    }

    // Convierte de DTO a Entity
    public Attribute attributeToEntity(AttributeDTO attributeDto) {

        // comprobamos si existe en la base de datos un objeto con el mismo id y si es asi lo retornamos
        if (attributeDto.getId() != null) {
            Optional<Attribute> existingAttribute = attributeRepository.findById(attributeDto.getId());
            if (existingAttribute.isPresent()) {
                System.out.println("attribute existe");
                Attribute attribute = existingAttribute.get(); // Retornar el Config existente
                attribute.setName(attributeDto.getName());

                return attribute;
            }
        }

        System.out.println("attribute no existe");
        // creamos un objeto attribute predeterminado
        Attribute attribute=new Attribute();

        // Mapeo de campos básicos
        attribute.setId(attributeDto.getId());
        // Mapeo de campos básicos
        attribute.setName(attributeDto.getName());

        // Mapeo de AttributeTypeId a un objeto AttributeType
        if (attributeDto.getAttributeTypeId() != null) {
            AttributeType attributeType = attributeTypeRepository.findById(attributeDto.getAttributeTypeId())// buscamos un attributeType por su id
                    .orElseGet(() -> {
                        // Si no se encuentra, crear un attributeType predeterminado
                        AttributeType newattributeTypeExample = new AttributeType();
                        // Mapeo de campos básicos a la entidad
                        newattributeTypeExample.setId(attributeDto.getAttributeTypeId());
                        newattributeTypeExample.setEnumDescription("Example");
                        newattributeTypeExample.setIsEnum(false);
                        newattributeTypeExample.setIsList(false);
                        newattributeTypeExample.setType("prueba");
                        newattributeTypeExample.setAttributes(null);
                        newattributeTypeExample.setAttributeTypeValues(null);
                        return attributeTypeRepository.save(newattributeTypeExample);// devolvemos el nuevo attributeType con datos por defecto
                    });
            attribute.setAttributeType(attributeType); //añadimos al attribute el attributeType
        }

        // Mapeo de configId a un objeto Config
        if (attributeDto.getConfigId() != null) {
            Config config = configRepository.findById(attributeDto.getConfigId())// buscamos un config por su id
                    .orElseGet(() -> {
                        // Si no se encuentra, crear un Config predeterminado
                        Config newConfigExample = new Config();
                        newConfigExample.setDescription("Default Config Description");
                        newConfigExample.setIsCustom(false);
                        newConfigExample.setDefaultValue("Default Value");
                        newConfigExample.setApplicationNode("Example Node");
                        newConfigExample.setParent(0L);
                        return configRepository.save(newConfigExample);// devolvemos el nuevo config con datos por defecto
                    });
            attribute.setConfig(config);//añadimos al attribute el config
        }

        // Guardar la entidad (ya sea una existente o una nueva)
        return attributeRepository.save(attribute);
    }
}
