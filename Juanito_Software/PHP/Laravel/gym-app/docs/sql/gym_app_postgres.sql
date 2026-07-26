-- =====================================================================
-- gym-app · Datos de desarrollo para PostgreSQL
-- ---------------------------------------------------------------------
-- Convertido desde el dump MySQL gym_app.sql (2026-04-22).
--
-- IMPORTANTE: este script contiene SOLO DATOS, no el esquema.
-- Las tablas debe crearlas Laravel antes de ejecutarlo:
--
--     php artisan migrate:fresh
--     psql -U postgres -d gym_app -f docs/sql/gym_app_postgres.sql
--
-- Motivo: el esquema es responsabilidad de las migraciones. Duplicarlo
-- aquí lo condenaría a desincronizarse, que es justo lo que le pasó al
-- dump original de MySQL.
--
-- Contraseña de todos los usuarios: la que tuvieran en su día (los
-- hashes bcrypt se conservan tal cual y siguen siendo válidos).
-- =====================================================================

-- El archivo está en UTF-8. Esto evita que la consola de Windows (CP850)
-- destroce los acentos al cargarlo.
SET client_encoding = 'UTF8';

BEGIN;

-- Limpieza previa (CASCADE respeta las claves foráneas)
TRUNCATE TABLE payments, inscriptions, classes, coaches, clients, users
    RESTART IDENTITY CASCADE;

-- ---------------------------------------------------------------------
-- users
-- ---------------------------------------------------------------------
INSERT INTO users (id, name, email, email_verified_at, phone_number, password, role, remember_token, created_at, updated_at) VALUES
(1,  'Juan Bernáldez Pereda',  'bernaldezperedaj@gmail.com', NULL, '638703514', '$2y$10$rBIE27QUXKo194lJYW5fdOW1q313NQhwJa6k9XQFOXOMS31GgHSky', 'admin',  NULL, '2025-10-24 03:03:07', '2025-10-24 03:03:07'),
(2,  'Entrenador1',            'entrenador1@prueba.com',     NULL, '645655668', '$2y$10$t5fhGijWEKD4MJg3yXRCtOWrS5Tl4GjceSuv6YfMV3mcyWVM.HhUy', 'coach',  NULL, '2025-10-24 09:44:06', '2025-11-23 10:38:23'),
(3,  'Prueba1',                'prueba@prueba.com',          NULL, '635656576', '$2y$10$cgB5Lj5925AjnXxaY5nN0ul01ykNRmg8KMIGwjlb3rYC0aCeSDICa', 'client', NULL, '2025-10-24 20:54:44', '2025-10-24 20:54:44'),
(4,  'Prueba2',                'prueba2@prueba.com',         NULL, '634565645', '$2y$10$kIuPRhKCNaLoKymR6ukGEOCqV4XJ6zUVdYyDNqXlG0M/Ac0/K6AT2', 'client', NULL, '2025-10-24 21:43:49', '2025-10-24 21:43:49'),
(20, 'Demo User Updated',      'demo@example.com',           NULL, '000000000', '$2y$10$P/CeapVCvLaTbAQX/QA0HOrcR52C8CEpvZwfN.zDadaIcUM0pcl2O', 'client', NULL, '2025-11-21 23:12:19', '2025-11-21 23:12:19'),
(21, 'Juan Bernáldez Pereda',  'juanbp300@gmail.com',        NULL, '657899889', '$2y$10$IzKMeUpA8n8UXQCPFPU7SezAfE44h6/L9Cd0qcY1ARica8jBg1/fe', 'client', NULL, '2025-11-23 09:07:46', '2025-11-23 09:07:46'),
(22, 'Prueba3',                'prueba3@prueba.com',         NULL, '645678767', '$2y$10$tM7i/UcMhP1uwxKyDjbix.6obK4bHCYxBIqxEC9ihs5rTrwKu1w96', 'client', NULL, '2025-11-23 10:36:34', '2025-11-23 10:37:37'),
(23, 'Entrenador2',            'Entrenador2@prueba.com',     NULL, '637898989', '$2y$10$68fPOZyJRNtYnj0XZCkRlust3y0a9tnHGn/B.h/MgBzo0c3fLfV/m', 'coach',  NULL, '2025-11-23 10:40:26', '2025-11-23 10:40:26'),
(24, 'Prueba4',                'prueba4@prueba.com',         NULL, '654565656', '$2y$10$IMnxeCC50Hskvk4g5T201epxcsjnuOw4Jcy7868wCJ/RKKrG35uJq', 'client', NULL, '2025-11-23 11:41:04', '2025-11-23 11:41:04'),
(25, 'prueba10',               'prueba10@prueba.com',        NULL, '645454546', '$2y$10$8Tu88mMn6ntCKT4TDvTjguuGuBjiU4BTNmm9Ncc4sVALYCmR0TwmS', 'client', NULL, '2025-11-25 15:14:31', '2025-11-25 15:14:58'),
(26, 'yyyy',                   'prueba@pruebayye.com',       NULL, '638703217', '$2y$10$eSR0S7ueiYPqC4bEOlA1bOkK49K7S5mUgCvmSZ3kqxQEjA42aSaSy', 'client', NULL, '2025-11-25 15:23:42', '2026-04-22 16:37:12'),
(27, 'mateo',                  'mateo@gmail.com',            NULL, '643454545', '$2y$10$WGd0PBzscOXUlkSD.YP2S.AgpsU2GPX9O8cEoCAvrjbUMUpAT.zLe', 'client', NULL, '2025-11-25 15:24:49', '2025-11-25 15:24:49'),
(28, 'Prueba7',                'prueba7@prueba.com',         NULL, '654545453', '$2y$10$eTYG1Sfw9ZWXZM9ufIV10ermfQBOcXYS52pj8syaRp/dtNZaA7Ig.', 'client', NULL, '2025-11-25 15:37:43', '2025-11-25 15:38:11'),
(30, 'paquito',                'paquito@gmail.com',          NULL, '657898338', '$2y$10$Mn17CdWIb8mIzXCfyGfnmuszAhrnvhKwuIXpg7AUdxZxk1w/UIwwW', 'coach',  NULL, '2026-04-22 16:38:22', '2026-04-22 16:41:40');

-- ---------------------------------------------------------------------
-- clients
-- ---------------------------------------------------------------------
INSERT INTO clients (id, user_id, name, email, phone_number, created_at, updated_at) VALUES
(1,  1,  'Juan Bernáldez Pereda', 'bernaldezperedaj@gmail.com', '638703514', '2025-10-24 03:03:07', '2025-10-24 03:03:07'),
(2,  3,  'Prueba1',               'prueba@prueba.com',          '635656576', '2025-10-24 20:54:44', '2025-10-24 20:54:44'),
(3,  4,  'Prueba2',               'prueba2@prueba.com',         '634565645', '2025-10-24 21:43:49', '2025-10-24 21:43:49'),
(16, 20, 'Demo Client Updated',   'client@example.com',         '000000000', '2025-11-21 23:12:19', '2025-11-21 23:12:19'),
(17, 21, 'Juan Bernáldez Pereda', 'juanbp300@gmail.com',        '657899889', '2025-11-23 09:07:46', '2025-11-23 09:07:46'),
(18, 22, 'Prueba3',               'prueba3@prueba.com',         '645678767', '2025-11-23 10:36:34', '2025-11-23 10:37:37'),
(19, 24, 'Prueba4',               'prueba4@prueba.com',         '654565656', '2025-11-23 11:41:04', '2025-11-23 11:41:04'),
(20, 25, 'prueba10',              'prueba10@prueba.com',        '645454546', '2025-11-25 15:14:31', '2025-11-25 15:14:58'),
(21, 26, 'yyyy',                  'prueba@pruebayye.com',       '638703217', '2025-11-25 15:23:42', '2026-04-22 16:37:12'),
(22, 27, 'mateo',                 'mateo@gmail.com',            '643454545', '2025-11-25 15:24:49', '2025-11-25 15:24:49'),
(23, 28, 'Prueba7',               'prueba7@prueba.com',         '654545453', '2025-11-25 15:37:43', '2025-11-25 15:38:11');

-- ---------------------------------------------------------------------
-- coaches
-- ---------------------------------------------------------------------
INSERT INTO coaches (id, user_id, name, email, phone_number, sport, created_at, updated_at) VALUES
(1,  2,  'Entrenador1',        'entrenador1@prueba.com', '645655668', 'boxeo',    '2025-10-24 09:44:06', '2025-11-23 10:38:23'),
(10, 20, 'Demo Coach Updated', 'coach@example.com',      '000000000', 'Boxeo',    '2025-11-21 23:12:19', '2025-11-21 23:12:19'),
(11, 23, 'Entrenador2',        'Entrenador2@prueba.com', '637898989', 'natacion', '2025-11-23 10:40:26', '2025-11-23 10:40:26'),
(12, 30, 'paquito',            'paquito@gmail.com',      '657898338', 'yoga',     '2026-04-22 16:38:22', '2026-04-22 16:41:40');

-- ---------------------------------------------------------------------
-- classes
-- Nota: "desc" va entrecomillado porque DESC es palabra reservada en SQL.
-- ---------------------------------------------------------------------
INSERT INTO classes (id, name, "desc", coach_id, days, init_hour, final_hour, created_at, updated_at) VALUES
(1,  'Boxeo',               'Clase de boxeo', 1,  'Martes y Jueves',          '17:00:00', '19:30:00', '2025-11-04 03:32:12', '2025-11-04 03:32:12'),
(6,  'Demo Classe Updated', NULL,             10, 'Lunes,Miércoles,Viernes',  '09:00:00', '11:00:00', '2025-11-21 23:12:19', '2026-04-22 16:49:34'),
(8,  'spinning',            'aaa',            1,  'Martes y Jueves',          '16:39:00', '17:39:00', '2025-11-23 10:39:27', '2025-11-23 10:39:27'),
(9,  'crossfit',            'bbb',            11, 'Viernes',                  '16:49:00', '17:49:00', '2025-11-23 10:49:39', '2025-11-23 10:49:39'),
(10, 'Waterpolo',           'waterpolo',      11, 'miercoles',                '14:57:00', '16:57:00', '2025-11-23 10:57:23', '2025-11-23 10:57:23'),
(11, 'zumba',               'zumba',          11, 'lunes',                    '05:05:00', '06:05:00', '2025-11-25 15:19:17', '2025-11-25 15:19:17'),
(12, 'futbol',              'aaa',            1,  'martes',                   '03:00:00', '05:00:00', '2025-11-25 15:32:52', '2025-11-25 15:32:52'),
(13, 'baloncesto',          'bbbb',           1,  'Martes y Jueves',          '04:00:00', '06:00:00', '2025-11-25 15:34:58', '2025-11-25 15:34:58');

-- ---------------------------------------------------------------------
-- inscriptions
-- ---------------------------------------------------------------------
INSERT INTO inscriptions (id, client_id, class_id, date, expires_at, created_at, updated_at) VALUES
(2,  3,  1, '2025-11-04', NULL,         '2025-11-04 03:51:44', '2025-11-04 03:51:44'),
(5,  16, 6, '2025-11-22', NULL,         '2025-11-21 23:12:19', '2025-11-21 23:12:19'),
(8,  3,  8, '2025-11-29', NULL,         '2025-11-23 10:40:51', '2025-11-23 10:40:51'),
(9,  3,  8, '2025-11-19', NULL,         '2025-11-23 10:50:35', '2025-11-23 10:50:35'),
(10, 3,  9, '2025-11-23', '2025-12-23', '2025-11-23 11:37:15', '2025-11-23 11:37:15'),
(12, 20, 1, '2025-11-25', '2025-12-25', '2025-11-25 15:15:48', '2025-11-25 15:15:48'),
(13, 23, 1, '2025-11-25', '2025-12-25', '2025-11-25 15:38:41', '2025-11-25 15:38:41');

-- ---------------------------------------------------------------------
-- payments
-- ---------------------------------------------------------------------
INSERT INTO payments (id, inscription_id, amount, date, created_at, updated_at) VALUES
(1, 2,  50.00,  '2025-11-04', '2025-11-04 05:20:55', '2025-11-04 05:20:55'),
(3, 5,  100.00, '2025-11-22', '2025-11-21 23:12:19', '2025-11-21 23:12:19'),
(4, 8,  30.00,  '2025-11-23', '2025-11-23 10:41:52', '2025-11-23 10:41:52'),
(5, 12, 50.00,  '2025-11-25', '2025-11-25 15:22:12', '2025-11-25 15:22:12'),
(6, 12, 50.00,  '2025-11-25', '2025-11-25 15:36:27', '2025-11-25 15:36:27');

-- ---------------------------------------------------------------------
-- Sincronizar las secuencias con los IDs insertados.
-- Sin esto, el primer INSERT desde la aplicación intentaría usar el id 1
-- y fallaría por clave duplicada.
-- ---------------------------------------------------------------------
SELECT setval(pg_get_serial_sequence('users',        'id'), COALESCE((SELECT MAX(id) FROM users),        1));
SELECT setval(pg_get_serial_sequence('clients',      'id'), COALESCE((SELECT MAX(id) FROM clients),      1));
SELECT setval(pg_get_serial_sequence('coaches',      'id'), COALESCE((SELECT MAX(id) FROM coaches),      1));
SELECT setval(pg_get_serial_sequence('classes',      'id'), COALESCE((SELECT MAX(id) FROM classes),      1));
SELECT setval(pg_get_serial_sequence('inscriptions', 'id'), COALESCE((SELECT MAX(id) FROM inscriptions), 1));
SELECT setval(pg_get_serial_sequence('payments',     'id'), COALESCE((SELECT MAX(id) FROM payments),     1));

COMMIT;
