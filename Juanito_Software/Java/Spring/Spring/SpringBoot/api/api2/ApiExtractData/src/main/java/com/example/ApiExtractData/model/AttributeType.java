package com.example.ApiExtractData.model;


import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonPOJOBuilder;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import jakarta.persistence.*;
import lombok.Data;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "attribute_type")
@Data
@JsonSerialize
@JsonDeserialize(builder = AttributeType.Builder.class)
// Entidad para Attribute
public class AttributeType extends AbstractEntity<Long> {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;


    @Column(name="enumDescription", length=255, nullable=false)
    private String enumDescription;
    @Column(name="isEnum", length=255, nullable=false)
    private Boolean isEnum;
    @Column(name="isList", nullable=false)
    private Boolean isList;
    @Column(name="type", length=255, nullable=false)
    private String type;

    //Relacion one to Many con Attribute (bidireccional)
    @OneToMany(mappedBy = "attributeType", cascade = CascadeType.ALL)
    @JsonBackReference
    private List<Attribute> attributes = new ArrayList<>();

    //Relacion one to Many con AttributeTypeValue (bidireccional)
    @OneToMany(mappedBy = "attributeType", cascade = CascadeType.ALL)
    @JsonManagedReference
    private List<AttributeTypeValue> attributeTypeValues = new ArrayList<>();


    // Constructor con parámetros
    public AttributeType(String enumDescription, Boolean isEnum, Boolean isList, String type, List<Attribute> attributes, List<AttributeTypeValue> attributeTypeValues) {
        super();
        this.enumDescription = enumDescription;
        this.isEnum = isEnum;
        this.isList = isList;
        this.type = type;
        this.attributes = attributes;
        this.attributeTypeValues = attributeTypeValues;
    }


    public AttributeType() {
        super();
    }

    @JsonPOJOBuilder
    static class Builder {
        @JsonProperty("enumDescription")
        String enumDescription;
        @JsonProperty("isEnum")
        Boolean isEnum;
        @JsonProperty("isList")
        Boolean isList;
        @JsonProperty("type")
        String type;

        @JsonProperty("attributes") // Añadido para serialización
        List<Attribute> attributes;

        @JsonProperty("attributeTypeValues") // Añadido para serialización
        List<AttributeTypeValue> attributeTypeValues;


        public AttributeType build() {
            return new AttributeType(enumDescription, isEnum, isList, type, attributes, attributeTypeValues); // Llamar al constructor actualizado
        }
    }

    public String getType() {
        return type;
    }
}


