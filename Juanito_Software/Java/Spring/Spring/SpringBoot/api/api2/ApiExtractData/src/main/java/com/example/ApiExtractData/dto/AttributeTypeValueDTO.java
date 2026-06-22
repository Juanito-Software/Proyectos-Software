package com.example.ApiExtractData.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor

// DTO para AttributeTypeValue
public class AttributeTypeValueDTO extends AbstractEntityDto {
    private Long id;
    private String description;
    private String value;
    private Long attributeTypeId; // Referencia al ID del AttributeType
}
