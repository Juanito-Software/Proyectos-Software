-- Crear la base de datos (esto debe hacerse manualmente o con un script adicional)
-- CREATE DATABASE game;

-- Crear usuarios (sin comprobación de existencia)
CREATE USER admin WITH PASSWORD 'P@ssw0rd1?';
CREATE USER client WITH PASSWORD 'sesamoPass1?';

-- Crear tipo nivel_privacidad (sin comprobación de existencia)
CREATE TYPE nivel_privacidad AS ENUM ('publico', 'privado', 'amigos');

-- Crear tablas (sin comprobación de existencia)
CREATE TABLE jugadores (
    id SERIAL PRIMARY KEY, 
    nombre VARCHAR(12) UNIQUE NOT NULL,
    email VARCHAR(50) UNIQUE,
    numtelefono VARCHAR(9) UNIQUE,
    password VARCHAR(256),
    refresh_token VARCHAR(255),
    rol VARCHAR(20) DEFAULT 'jugador'
);

-- Tabla de puntuaciones (original) con restricción UNIQUE en jugador_id
CREATE TABLE puntuaciones (
    id SERIAL PRIMARY KEY, 
    valor INTEGER NOT NULL, 
    jugador_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
);

-- Nueva tabla para almacenar el histórico de puntuaciones sin restricción UNIQUE, permitiendo múltiples registros por jugador.
CREATE TABLE puntuaciones_historico (
    id SERIAL PRIMARY KEY,
    valor INTEGER NOT NULL,
    jugador_id INTEGER NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
);

CREATE TABLE privacidad (
    id SERIAL PRIMARY KEY, 
    nivel_de_privacidad nivel_privacidad NOT NULL DEFAULT 'publico',
    jugador_id INTEGER NOT NULL,
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id) ON DELETE CASCADE
);

CREATE TABLE amistades (
    id SERIAL PRIMARY KEY, 
    jugador_solicitante_id INTEGER NOT NULL,
    jugador_receptor_id INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    FOREIGN KEY (jugador_solicitante_id) REFERENCES jugadores(id) ON DELETE CASCADE,
    FOREIGN KEY (jugador_receptor_id) REFERENCES jugadores(id) ON DELETE CASCADE
);

CREATE TABLE logros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL
);

CREATE TABLE logros_jugadores (
    id SERIAL PRIMARY KEY,
    jugador_id INT NOT NULL,
    logro_id INT NOT NULL,
    fecha_obtenido TIMESTAMP NOT NULL,
    CONSTRAINT fk_jugador FOREIGN KEY (jugador_id) REFERENCES jugadores(id),
    CONSTRAINT fk_logro FOREIGN KEY (logro_id) REFERENCES logros(id)
);

-- Conceder privilegios
GRANT ALL PRIVILEGES ON DATABASE game TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;
GRANT ALL PRIVILEGES ON TABLE jugadores TO admin;
GRANT ALL PRIVILEGES ON TABLE puntuaciones TO admin;
GRANT ALL PRIVILEGES ON TABLE puntuaciones_historico TO admin;
GRANT ALL PRIVILEGES ON TABLE privacidad TO admin;
GRANT ALL PRIVILEGES ON TABLE amistades TO admin;
GRANT ALL PRIVILEGES ON TABLE logros TO admin;
GRANT ALL PRIVILEGES ON TABLE logros_jugadores TO admin;

GRANT CONNECT ON DATABASE game TO client;
GRANT USAGE ON SCHEMA public TO client;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO client;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO client;
GRANT SELECT, INSERT, UPDATE ON TABLE jugadores TO client;
GRANT SELECT, INSERT, UPDATE ON TABLE puntuaciones TO client;
GRANT SELECT, INSERT, UPDATE ON TABLE puntuaciones_historico TO client;
GRANT SELECT, INSERT, UPDATE ON TABLE privacidad TO client;
GRANT SELECT, INSERT, UPDATE ON TABLE amistades TO client;
GRANT SELECT, INSERT, UPDATE ON TABLE logros_jugadores TO client;

GRANT DELETE ON TABLE jugadores TO client;
GRANT DELETE ON TABLE amistades TO client;
