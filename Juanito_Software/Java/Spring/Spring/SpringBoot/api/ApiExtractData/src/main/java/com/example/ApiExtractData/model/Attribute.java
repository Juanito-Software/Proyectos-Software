package com.example.ApiExtractData.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonPOJOBuilder;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import jakarta.persistence.*;
import lombok.Data;

import java.util.List;

/**
 * Entidad que representa un atributo en el sistema.
 *
 * Esta clase define los atributos básicos de un `Attribute` junto con su relación con
 * otros componentes como `AttributeType`. Es utilizada en la persistencia de datos en la base de datos y
 * en la serialización/deserialización JSON.
 */

@Entity
@Table(name = "attribute")
@Data
@JsonSerialize
@JsonDeserialize(builder = Attribute.Builder.class)
public class Attribute  extends AbstractEntity<Long> {

    /**
     * Identificador único de cada atributo.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Nombre del atributo, debe ser único y no nulo.
     */
    @Column(name="name", length=255, nullable=false)
    private String name;

    /**
     * Relación Many-to-One con `AttributeType`, representa el tipo de atributo al que pertenece.
     * Configurada como relación bidireccional.
     */
    @ManyToOne
    @JoinColumn(name = "attribute_type", referencedColumnName = "id")
    @JsonManagedReference
    private AttributeType attributeType;


    /**
     * Constructor completo que inicializa un `Attribute` con el nombre y el tipo de atributo.
     *
     * @param name Nombre del atributo.
     * @param attributeType Tipo de atributo asociado.
     */
    public Attribute( String name, AttributeType attributeType) {
        super();
        this.name = name;
        this.attributeType = attributeType;
    }

    /**
     * Constructor por defecto sin argumentos necesario para la creación de instancias sin inicialización.
     */
    public Attribute(){
        super();
    }

    /**
     * Builder para la clase {@link Attribute} que facilita la construcción de instancias
     * a partir de JSON, utilizando la deserialización JSON con Jackson.
     */
    @JsonPOJOBuilder
    static class Builder {
        @JsonProperty("name")
        String name;
        @JsonProperty("attribute_type")
        AttributeType attributeType;


        public Attribute build() {
            return new Attribute(name,attributeType);
        }
    }
}