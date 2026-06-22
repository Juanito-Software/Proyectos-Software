package com.example.ApiExtractData.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Set;


@Data
@NoArgsConstructor
@AllArgsConstructor

// DTO para Config
public class ConfigDTO extends AbstractEntityDto {
    private Long id;
    private String description;

    @JsonProperty("is_custom") // Esto mapeará el campo is_custom en JSON a isCustom en el DTO
    private Boolean isCustom;
    @JsonProperty("default_value")
    private String defaultValue;
    @JsonProperty("application_node")
    private String applicationNode;
    @JsonProperty("parent")
    private Long parent;
    private List<Long> attributeIds;

    // Getters y setters

}
