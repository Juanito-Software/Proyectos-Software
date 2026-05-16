CREATE TABLE usuario (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE locutor (
    id BIGSERIAL PRIMARY KEY,
    nombre_artistico VARCHAR(255),
    usuario_id BIGINT NOT NULL REFERENCES usuario (id) ON DELETE CASCADE
);

CREATE TABLE programa (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(255),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE programa_locutor (
    programa_id BIGINT NOT NULL REFERENCES programa (id) ON DELETE CASCADE,
    locutor_id BIGINT NOT NULL REFERENCES locutor (id) ON DELETE CASCADE,
    PRIMARY KEY (programa_id, locutor_id)
);

CREATE TABLE emision (
    id BIGSERIAL PRIMARY KEY,
    programa_id BIGINT NOT NULL REFERENCES programa (id) ON DELETE CASCADE,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio TIMESTAMP NOT NULL,
    hora_fin TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL
);

CREATE TABLE comentario (
    id BIGSERIAL PRIMARY KEY,
    emision_id BIGINT NOT NULL REFERENCES emision (id) ON DELETE CASCADE,
    autor VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    estado VARCHAR(20) NOT NULL
);

CREATE TABLE chat_message (
    id BIGSERIAL PRIMARY KEY,
    emision_id BIGINT NOT NULL REFERENCES emision (id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
