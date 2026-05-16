-- Datos de demo (el admin se crea al arrancar la API: admin@radiostack.local / admin123)

INSERT INTO usuario (id, nombre, email, password_hash, rol, activo) VALUES
(1, 'Carlos Ruiz', 'carlos@radiostack.com', 'demo', 'ADMIN', true),
(2, 'Lucia Moreno', 'lucia@radiostack.com', 'demo', 'LOCUTOR', true);

INSERT INTO locutor (id, nombre_artistico, usuario_id) VALUES
(1, 'DJ Carlos', 1),
(2, 'Lucia FM', 2);

INSERT INTO programa (id, nombre, descripcion, categoria, activo) VALUES
(1, 'Morning Beats', 'Programa musical matinal', 'MUSICA', true),
(2, 'Noticias 24', 'Noticias y actualidad', 'NOTICIAS', true),
(3, 'Late Night Mix', 'Sesion nocturna electronica', 'MUSICA', true);

INSERT INTO programa_locutor (programa_id, locutor_id) VALUES
(1, 1),
(2, 2),
(3, 1);

INSERT INTO emision (id, programa_id, dia_semana, hora_inicio, hora_fin, estado) VALUES
(1, 1, 'LUNES', '2026-05-10 08:00:00', '2026-05-10 10:00:00', 'PROGRAMADO'),
(2, 2, 'MARTES', '2026-05-11 12:00:00', '2026-05-11 13:00:00', 'PROGRAMADO'),
(3, 3, 'VIERNES', '2026-05-15 22:00:00', '2026-05-16 00:00:00', 'PROGRAMADO');

SELECT setval(pg_get_serial_sequence('usuario', 'id'), (SELECT COALESCE(MAX(id), 1) FROM usuario));
SELECT setval(pg_get_serial_sequence('locutor', 'id'), (SELECT COALESCE(MAX(id), 1) FROM locutor));
SELECT setval(pg_get_serial_sequence('programa', 'id'), (SELECT COALESCE(MAX(id), 1) FROM programa));
SELECT setval(pg_get_serial_sequence('emision', 'id'), (SELECT COALESCE(MAX(id), 1) FROM emision));
