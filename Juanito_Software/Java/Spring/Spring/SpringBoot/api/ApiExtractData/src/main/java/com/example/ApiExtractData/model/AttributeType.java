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

/**
 * Entidad que representa un tipo de atributo en el sistema.
 *
 * Define las propiedades y características de un tipo de atributo, como si es un enumerador o una lista.
 * También se utiliza en la relación con la entidad {@link Attribute} para establecer un vínculo bidireccional.
 */

@Entity
@Table(name = "attribute_type")
@Data
@JsonSerialize
@JsonDeserialize(builder = AttributeType.Builder.class)
public class AttributeType extends AbstractEntity<Long> {

    /**
     * Identificador único para cada tipo de atributo.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Descripción del enumerador si el atributo es de tipo enum.
     */
    @Column(name="enumDescription", length=255, nullable=true)
    private String enumDescription;

    /**
     * Indica si el tipo de atributo es un enumerador.
     */
    @Column(name="isEnum", length=255, nullable=true)
    private Boolean isEnum;

    /**
     * Indica si el tipo de atributo es una lista.
     */
    @Column(name="isList", nullable=true)
    private Boolean isList;

    /**
     * Tipo específico del atributo, almacenado como una cadena.
     */
    @Column(name="type", length=255, nullable=false)
    private String type;

    /**
     * Lista de atributos asociados a este tipo de atributo.
     * Relación bidireccional de One-to-Many con {@link Attribute}.
     * Evita la recursión infinita con la anotación {@link JsonBackReference}.
     */
    @OneToMany(mappedBy = "attributeType", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonBackReference // Evita la recursión infinita en el lado de AttributeType
    private List<Attribute> attributes;

    /**
     * Constructor completo que permite inicializar un `AttributeType` con todos sus campos.
     *
     * @param enumDescription Descripción del enumerador.
     * @param isEnum Indica si el tipo de atributo es un enumerador.
     * @param isList Indica si el tipo de atributo es una lista.
     * @param type Tipo específico del atributo.
     */
    public AttributeType(String enumDescription, Boolean isEnum, Boolean isList, String type) {
        super();
        this.enumDescription = enumDescription;
        this.isEnum = isEnum;
        this.isList = isList;
        this.type = type;
    }

    /**
     * Constructor sin parámetros necesario para la creación de instancias sin inicialización.
     */
    public AttributeType() {
        super();
    }

    /**
     * Devuelve si el tipo de atributo es una lista.
     *
     * @return Booleano que indica si el tipo de atributo es una lista.
     */
    public Boolean getList() {
        return isList;
    }

    /**
     * Devuelve si el tipo de atributo es un enumerador.
     *
     * @return Booleano que indica si el tipo de atributo es un enumerador.
     */
    public Boolean getEnum() {
        return isEnum;
    }

    /**
     * Builder para la clase {@link AttributeType} que facilita la construcción de instancias
     * a partir de JSON, utilizando la deserialización JSON con Jackson.
     */
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

        public AttributeType build() {
            return new AttributeType(enumDescription, isEnum, isList, type); // Llamar al constructor actualizado
        }
    }
}


