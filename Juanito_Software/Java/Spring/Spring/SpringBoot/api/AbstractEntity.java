package es.snc.emi.config.api.utils;

import java.io.Serializable;
import java.time.ZoneId;
import java.time.ZonedDateTime;

import javax.persistence.Column;
import javax.persistence.MappedSuperclass;
import javax.persistence.PrePersist;
import javax.persistence.PreUpdate;
import javax.persistence.Version;

import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@EqualsAndHashCode
@NoArgsConstructor
@MappedSuperclass
public abstract class AbstractEntityConfig<K extends Serializable> {

	/**
	 * Default version lock (for optimistic locking) for new entities 
	 */
	private static final Integer DEFAULT_VERSION_LOCK = 1;
	
	/**
	 * Default deleted property for new entities
	 */
	private static final Boolean DEFAULT_DELETED = Boolean.FALSE;

	/**
	 *  Database entity version, for controlling optimistic locking
	 */
	@Version
	@Column(name = "VERSION_LOCK", nullable = false)
	private Integer versionLock;

	/**
	 * Indicates if the entity was soft-deleted
	 */
	@Column(name = "DELETED", nullable = false)
	private Boolean deleted;
	
	/**
	 * Date when entity was created (always UTC)
	 */
	@Column(name = "CREATED_AT", nullable = false, updatable = false)
	private ZonedDateTime createdAt;

	/**
	 * Date when entity was last updated (always UTC)
	 */
	@Column(name = "MODIFIED_AT", nullable = true)
	private ZonedDateTime modifiedAt;

	@PrePersist
    private void onPrePersist() {
        
		this.deleted = DEFAULT_DELETED;
		this.versionLock = DEFAULT_VERSION_LOCK;
		this.createdAt = ZonedDateTime.now(ZoneId.of("UTC"));
		this.modifiedAt = this.createdAt;
    }

    @PreUpdate
    private void onPreUpdate() {
        
    	this.modifiedAt = ZonedDateTime.now(ZoneId.of("UTC"));
    }
}
