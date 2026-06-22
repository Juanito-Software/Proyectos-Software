package es.snc.emi.config.api.utils;


import javax.validation.constraints.NotNull;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@EqualsAndHashCode
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public abstract class AbstractEntityDtoConfig {
	
	/**
	 * Linked database entity version, for controlling optimistic locking
	 */
	@NotNull
//	@JsonProperty(access = JsonProperty.Access.READ_ONLY)
	private Integer versionLock;
	
	/**
	 * Indicates if the entity was soft-deleted
	 */
	@NotNull
//	@JsonProperty(access = JsonProperty.Access.READ_ONLY)
	private Boolean deleted;
	
	/**
	 * Date when entity was created (always UTC)
	 */
	@JsonProperty(access = JsonProperty.Access.READ_ONLY)
	private String createdAt;

	/**
	 * Date when entity was last updated (always UTC)
	 */
	@JsonProperty(access = JsonProperty.Access.READ_ONLY)
	private String modifiedAt;
}
