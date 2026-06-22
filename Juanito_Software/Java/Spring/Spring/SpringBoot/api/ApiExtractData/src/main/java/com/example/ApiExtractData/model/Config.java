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
import java.util.Set;

/**
 * Representa una entidad de configuración en la aplicación, que permite definir configuraciones
 * personalizables con jerarquías y atributos específicos.
 */

@Entity
@Table(name = "config")
@Data
@JsonSerialize
@JsonDeserialize(builder = Config.Builder.class)
public class Config extends AbstractEntity<Long> {

    /**
     * Identificador único de la configuración.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Descripción de la configuración.
     */
    @Column(name = "description", length = 255, nullable = true)
    private String description;

    /**
     * Indica si la configuración es personalizada.
     */
    @Column(name = "is_custom", length = 255, nullable = true)
    private Boolean isCustom;

    /**
     * Valor predeterminado de la configuración.
     */
    @Column(name = "default_value", length = 255, nullable = true)
    private String defaultValue;

    /**
     * Nodo de aplicación asociado a la configuración.
     */
    @Column(name = "application_node", length = 255, nullable = true)
    private Long applicationNode;

    /**
     * ID del padre de esta configuración, en caso de ser parte de una jerarquía.
     */
    // Este campo indica el ID del Config padre
    @Column(name = "parent")
    private Long parent_Id;

    /**
     * Configuración padre en una relación bidireccional, utilizada para modelar jerarquías de configuración.
     */
    // Relación bidireccional con el "Config" padre
    @ManyToOne
    @JoinColumn(name = "parent", insertable = false, updatable = false)
    @JsonBackReference // Evita la recursión infinita en la serialización
    private Config parent;

    /**
     * Lista de configuraciones hijas en una relación jerárquica con esta configuración.
     */
    // Relación OneToMany con los hijos de esta configuración
    @OneToMany(mappedBy = "parent", orphanRemoval = true)
    @JsonBackReference // Esta es la parte que permite la serialización de los hijos
    private List<Config> children;

    /**
     * Atributo asociado a esta configuración.
     */
    //Relacion one to Many con Attribute
    @ManyToOne//orphanRemoval = true: al desasociar una entidad secundaria de la principal, se elimina automáticamente de la base de datos.
    @JoinColumn(name = "attribute_id", insertable = false, updatable = false)
    @JsonManagedReference
    private Attribute attribute;

    /**
     * Constructor completo para inicializar una configuración con todos sus atributos.
     *
     * @param description     Descripción de la configuración.
     * @param isCustom        Indica si la configuración es personalizada.
     * @param defaultValue    Valor predeterminado de la configuración.
     * @param applicationNode Nodo de aplicación asociado.
     * @param parent_Id       ID de la configuración padre.
     * @param attribute       Atributo asociado a esta configuración.
     */
    public Config(String description, Boolean isCustom, String defaultValue, Long applicationNode, Long parent_Id, Attribute attribute) {
        super();
        this.description = description;
        this.isCustom = isCustom;
        this.defaultValue = defaultValue;
        this.applicationNode = applicationNode;
        this.parent_Id = parent_Id;
        this.attribute = attribute;
    }

    /**
     * Constructor por defecto.
     */
    public Config() {
        super();
    }

    /**
     * Builder para la clase {@link Config} que facilita la construcción de instancias
     * a partir de JSON, utilizando la deserialización JSON con Jackson.
     */
    @JsonPOJOBuilder
    static class Builder {
        @JsonProperty("description")
        String description;
        @JsonProperty("is_custom")
        Boolean isCustom;
        @JsonProperty("default_value")
        String defaultValue;
        @JsonProperty("application_node")
        Long applicationNode;
        @JsonProperty("parent")
        Long parentId;
        @JsonProperty("attributes")
        Attribute attribute;

        /**
         * Construye una instancia de {@link Config} utilizando los valores establecidos en el Builder.
         *
         * @return Nueva instancia de {@link Config}.
         */
        public Config build() {
            return new Config(description, isCustom, defaultValue, applicationNode, parentId, attribute);
        }
    }
}