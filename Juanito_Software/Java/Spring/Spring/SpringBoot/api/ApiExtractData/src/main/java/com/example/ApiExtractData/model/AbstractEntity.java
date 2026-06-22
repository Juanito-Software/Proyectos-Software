package com.example.ApiExtractData.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.persistence.*;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.io.Serializable;
import java.time.ZoneId;
import java.time.ZonedDateTime;

@Getter
@Setter
@EqualsAndHashCode
@NoArgsConstructor

@MappedSuperclass
// Clase abstracta de la que extienden las entidades
public class AbstractEntity<K extends Serializable> {
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
    @Column(name = "version_lock", nullable = false)
    private Integer versionLock = 1;

    /**
     * Indicates if the entity was soft-deleted
     */
    @Column(name = "deleted", nullable = false)
    private Boolean deleted = false;

    /**
     * Date when entity was created (always UTC)
     */
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    @Column(name = "created_at", nullable = false, updatable = false)
    private ZonedDateTime createdAt;

    /**
     * Date when entity was last updated (always UTC)
     */
    @JsonFormat(shape = JsonFormat.Shape.STRING, pattern = "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
    @Column(name = "modified_at", nullable = true)
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

