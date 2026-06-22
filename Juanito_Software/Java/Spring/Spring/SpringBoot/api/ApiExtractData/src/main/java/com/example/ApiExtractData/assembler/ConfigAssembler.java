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
        configDTO.setDescription(config.getDescription());
        configDTO.setIsCustom(config.getIsCustom());
        configDTO.setDefaultValue(config.getDefaultValue());
        configDTO.setApplicationNode(config.getApplicationNode());

        return configDTO;
    }

    // Metodo para convertir un ConfigDTO a la entidad Config
    public Config configToEntity(ConfigDTO configDTO) {


        // Si no se encuentra, crear un config predeterminado
        Config config = new Config();// creamos una instancia de la entidad Config

        // Mapeo de campos básicos a la entidad
        config.setDescription(configDTO.getDescription());
        config.setIsCustom(configDTO.getIsCustom());
        config.setDefaultValue(configDTO.getDefaultValue());
        config.setApplicationNode(configDTO.getApplicationNode());

        return config;
    }
}