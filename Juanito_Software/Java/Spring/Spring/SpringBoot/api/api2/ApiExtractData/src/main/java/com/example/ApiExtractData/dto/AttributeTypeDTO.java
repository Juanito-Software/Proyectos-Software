package com.example.ApiExtractData.dto;

import lombok.*;

import java.util.List;

@Data
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor

// DTO para AttributeType
public class AttributeTypeDTO extends AbstractEntityDto {
    private Long id;
    private String enumDescription;
    private Boolean isEnum;
    private Boolean isList;
    private String type;
    private List<Long> attributeIds; // IDs de los valores asociados
    private List<Long> attributeTypeValueIds; // IDs de los valores asociados
}
