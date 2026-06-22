package com.example.ApiExtractData.assembler;

import com.example.ApiExtractData.dto.ConfigDTO;
import com.example.ApiExtractData.model.Attribute;
import com.example.ApiExtractData.model.Config;
import com.example.ApiExtractData.repository.AttributeRepository;
import com.example.ApiExtractData.repository.ConfigRepository;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

@Component
public class ConfigAssembler {


    private final AttributeRepository attributeRepository;
    private final ConfigRepository configRepository;

    public ConfigAssembler(AttributeRepository attributeRepository, ConfigRepository configRepository) {
        this.attributeRepository = attributeRepository;
        this.configRepository = configRepository;
    }

    // Metodo para convertir una entidad Config a ConfigDTO
    public ConfigDTO configToDTO(Config config) {

        ConfigDTO configDTO = new ConfigDTO();// creamos una instancia del DTO ConfigDTO
        // Mapeo de campos básicos al DTO
        configDTO.setId(config.getId());
        configDTO.setDescription(config.getDescription());
        configDTO.setIsCustom(config.getIsCustom());
        configDTO.setDefaultValue(config.getDefaultValue());
        configDTO.setApplicationNode(config.getApplicationNode());
        configDTO.setParent(config.getParent());

        // Mapeo de objetos attribute a sus IDs
        List<Long> attributeIds = config.getAttributes().stream() // Crea un flujo (stream) de los atributos (Attribute) de config
                .map(Attribute::getId) //aplica el metodo getId() a cada objeto Attribute en el flujo, transformando cada atributo en su ID (Long).
                .collect(Collectors.toList()); // recopila todos los IDs mapeados en una lista (List<Long>) y asigna el resultado a attributeIds.
        configDTO.setAttributeIds(attributeIds);// Añade los attributeIds al dto

        return configDTO;
    }

    // Metodo para convertir un ConfigDTO a la entidad Config
    public Config configToEntity(ConfigDTO configDTO) {

        // comprobamos si existe en la base de datos un objeto con el mismo id y si es asi lo retornamos
        if (configDTO.getId() != null) {
            Optional<Config> existingConfig = configRepository.findById(configDTO.getId());
            if (existingConfig.isPresent()) {
                System.out.println("config existe");
                Config config = existingConfig.get(); // Retornar el Config existente
                config.setDescription(configDTO.getDescription());
                config.setIsCustom(configDTO.getIsCustom());
                config.setDefaultValue(configDTO.getDefaultValue());
                config.setApplicationNode(configDTO.getApplicationNode());
                config.setParent(configDTO.getParent());

                // Actualizar los atributos si el Config ya existe
                List<Attribute> attributes = configDTO.getAttributeIds().stream()
                        .map(attributeRepository::findById)
                        .filter(Optional::isPresent)
                        .map(Optional::get)
                        .collect(Collectors.toList());
                config.setAttributes(attributes);

                return config;
            }
        }

        System.out.println("config no existe");
        // Si no se encuentra, crear un config predeterminado
        Config config = new Config();// creamos una instancia de la entidad Config

        // Mapeo de campos básicos a la entidad
        config.setId(configDTO.getId());
        config.setDescription(configDTO.getDescription());
        config.setIsCustom(configDTO.getIsCustom());
        config.setDefaultValue(configDTO.getDefaultValue());
        config.setApplicationNode(configDTO.getApplicationNode());
        config.setParent(configDTO.getParent());

        // Mapeo de attributeIds a un conjunto de objetos Attribute
        List<Attribute> attributes = configDTO.getAttributeIds().stream()
                .map(attributeRepository::findById)
                .filter(Optional::isPresent)
                .map(Optional::get)
                .collect(Collectors.toList());
        config.setAttributes(attributes);

        return config;
    }
}