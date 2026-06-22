package com.example.ApiExtractData.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonPOJOBuilder;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import jakarta.persistence.*;
import lombok.Data;
import lombok.Setter;

import java.util.Objects;

@Entity
@Table(name = "attribute_type_value")
@Data
@JsonSerialize
@JsonDeserialize(builder = AttributeTypeValue.Builder.class)
// Entidad para AttributeTypeValue
public class AttributeTypeValue extends AbstractEntity<Long>{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name="description", length=255, nullable=false)
    private String description;
    @Column(name="value", length=255, nullable=false)
    private String value;

    //Relacion Many to one con AttributeType (bidireccional)
    @Setter
    @ManyToOne
    @JoinColumn(name = "attribute_type_id", referencedColumnName = "id")
    @JsonBackReference
    private AttributeType attributeType;


    public AttributeTypeValue(String description, String value, AttributeType attributeType) {
        super();
        this.description = description;
        this.value = value;
        this.attributeType = attributeType; // Añadido al constructor
    }

    public AttributeTypeValue() {
        super();
    }

    @JsonPOJOBuilder
    static class Builder {
        @JsonProperty("description")
        String description;
        @JsonProperty("value")
        String value;
        @JsonProperty("attributeType") // Añadido para serialización
        AttributeType attributeType;


        public AttributeTypeValue build() {
            return new AttributeTypeValue(description, value, attributeType);
        }
    }
}

