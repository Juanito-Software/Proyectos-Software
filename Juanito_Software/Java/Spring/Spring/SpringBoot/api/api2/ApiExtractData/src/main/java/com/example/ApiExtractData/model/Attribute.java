package com.example.ApiExtractData.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.databind.annotation.JsonPOJOBuilder;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;
import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "attribute")
@Data
@JsonSerialize
@JsonDeserialize(builder = Attribute.Builder.class)

// Entidad para Attribute
public class Attribute  extends AbstractEntity<Long> {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;


    @Column(name="name", length=255, nullable=false)
    private String name;

    //Relacion Many to one con AttributeType (bidireccional)
    @ManyToOne(cascade = CascadeType.ALL)//cascade = CascadeType.ALL: todas las operaciones de persistencia realizadas en la entidad padre se aplicaran automaticamentete sobre la entidad hija
    @JoinColumn(name = "attribute_type_id", referencedColumnName = "id")
    @JsonManagedReference
    private AttributeType attributeType;

    //Relacion Many to one con Config (bidireccional)
    @ManyToOne(cascade = CascadeType.ALL)
    @JoinColumn(name = "config_id", referencedColumnName = "id")
    @JsonBackReference
    private Config config;

    public Attribute( String name, AttributeType attributeType, Config config) {
        super();
        this.name = name;
        this.attributeType = attributeType;
        this.config = config;
    }


    public Attribute(){
        super();
    }

    @JsonPOJOBuilder
    static class Builder {
        @JsonProperty("name")
        String name;
        @JsonProperty("attributeType")
        AttributeType attributeType;
        @JsonProperty("config")
        Config config;

        public Attribute build() {
            return new Attribute(name,attributeType,config);
        }
    }
}