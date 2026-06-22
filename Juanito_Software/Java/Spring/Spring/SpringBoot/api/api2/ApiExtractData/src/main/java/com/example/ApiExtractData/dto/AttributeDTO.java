package com.example.ApiExtractData.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor

// DTO para Attribute
public class AttributeDTO extends AbstractEntityDto{
    private Long id;
    private String name;
    private Long attributeTypeId;  // Referencia al ID del AttributeType
    private Long configId;         // Referencia al ID del Config
}
