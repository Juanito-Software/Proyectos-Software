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

/**
 * Entidad que representa un valor de tipo de atributo en el sistema.
 *
 * Define los valores específicos de un tipo de atributo, incluyendo su descripción y su valor.
 * Está relacionado con la entidad {@link AttributeType} en una relación Many-to-One.
 */

@Entity
@Table(name = "attribute_type_value")
@Data
@JsonSerialize
@JsonDeserialize(builder = AttributeTypeValue.Builder.class)
public class AttributeTypeValue extends AbstractEntity<Long>{

    /**
     * Identificador único para cada valor de tipo de atributo.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Descripción del valor de tipo de atributo.
     */
    @Column(name="description", length=255, nullable=true)
    private String description;

    /**
     * Valor específico del tipo de atributo.
     */
    @Column(name="value", length=255, nullable=false)
    private String value;


    /**
     * Relación Many-to-One con {@link AttributeType}, estableciendo el tipo de atributo
     * al que pertenece este valor. Se utiliza {@link JsonBackReference} para evitar la
     * recursión infinita en la serialización JSON.
     */
    @Setter
    @ManyToOne
    @JoinColumn(name = "attribute_type", referencedColumnName = "id")
    @JsonBackReference
    private AttributeType attributeType;

    /**
     * Constructor que permite inicializar un `AttributeTypeValue` con todos sus campos.
     *
     * @param description Descripción del valor de tipo de atributo.
     * @param value Valor específico del tipo de atributo.
     * @param attributeType Tipo de atributo al que pertenece este valor.
     */
    public AttributeTypeValue(String description, String value, AttributeType attributeType) {
        super();
        this.description = description;
        this.value = value;
        this.attributeType = attributeType; // Añadido al constructor
    }

    /**
     * Constructor sin parámetros necesario para la creación de instancias sin inicialización.
     */
    public AttributeTypeValue() {
        super();
    }

    /**
     * Builder para la clase {@link AttributeTypeValue} que facilita la construcción de instancias
     * a partir de JSON, utilizando la deserialización JSON con Jackson.
     */
    @JsonPOJOBuilder
    static class Builder {
        @JsonProperty("description")
        String description;
        @JsonProperty("value")
        String value;
        @JsonProperty("attribute_type") // Añadido para serialización
        AttributeType attributeType;


        public AttributeTypeValue build() {
            return new AttributeTypeValue(description, value, attributeType);
        }
    }
}

