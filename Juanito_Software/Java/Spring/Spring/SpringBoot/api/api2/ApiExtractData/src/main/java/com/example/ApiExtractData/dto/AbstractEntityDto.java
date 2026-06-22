package com.example.ApiExtractData.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotNull;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@EqualsAndHashCode
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)

// Clase abstracta de la que extienden los DTOs
public class AbstractEntityDto {
    /**
     * Linked database entity version, for controlling optimistic locking
     */
    @NotNull
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private Integer versionLock = 1;

    /**
     * Indicates if the entity was soft-deleted
     */
    @NotNull
	@JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private Boolean deleted=false;

    /**
     * Date when entity was created (always UTC)
     */
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private String createdAt;

    /**
     * Date when entity was last updated (always UTC)
     */
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    @JsonProperty(access = JsonProperty.Access.READ_ONLY)
    private String modifiedAt;
}
