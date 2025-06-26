-- (Opcional) Crea la base de datos si no existe
-- Ejecuta esto fuera si estás conectado al servidor principal
-- CREATE DATABASE mydb;

-- Usa la base de datos
-- \c mydb

-- Crea la tabla 'persona_lectura'
CREATE TABLE IF NOT EXISTS persona (
    id              INTEGER PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    apellido        VARCHAR(100) NOT NULL,
    edad            INTEGER CHECK (edad >= 0),
    email           VARCHAR(150),
    telefono        BIGINT,
    ciudad          VARCHAR(100),
    pais            VARCHAR(100),
    direccion       TEXT,
    fecha_registro  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
