# 🏆 Sistema de Leaderboard para Juego en Unity

**Autor:** Juan Bernáldez Pereda · **DNI:** 72231203W · **Versión:** 1.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3 / C#

**Proyecto de Fin de Grado (TFG)** - Desarrollo de Aplicaciones Multiplataforma (DAM)  
**Curso Académico:** 2024/2025 · **Fecha:** 28 de Septiembre de 2024

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Objetivos](#objetivos)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Arquitectura del Sistema](#arquitectura-del-sistema)
5. [Requisitos e Instalación](#requisitos-e-instalación)
6. [Configuración](#configuración)
7. [Estructura del Proyecto](#estructura-del-proyecto)
8. [Uso y Ejecución](#uso-y-ejecución)
9. [Funcionalidades Principales](#funcionalidades-principales)
10. [Base de Datos](#base-de-datos)
11. [API REST Endpoints](#api-rest-endpoints)
12. [Seguridad](#seguridad)
13. [Despliegue](#despliegue)
14. [Troubleshooting](#troubleshooting)
15. [Contribuciones Futuras](#contribuciones-futuras)
16. [Contacto](#contacto)

---

## 🧾 Descripción General

**Sistema de Leaderboard para Juego en Unity** es una solución completa de **gestión de puntuaciones** diseñada para videojuegos desarrollados en Unity. El sistema permite a los jugadores comparar su rendimiento, gestionar amigos, controlar privacidad y acceder a un ranking global en tiempo real.

El proyecto implementa una arquitectura de **tres capas**:
- **Frontend:** Cliente en Unity (C#)
- **Backend:** API REST en Flask (Python)
- **Persistencia:** Base de datos PostgreSQL

Este sistema fue desarrollado como proyecto académico de fin de grado y demoestra competencias en arquitectura de aplicaciones, desarrollo fullstack, autenticación segura y bases de datos relacionales.

---

## 🎯 Objetivos

### Objetivo General

Desarrollar un sistema completo de Leaderboard que permita la gestión de puntuaciones para un videojuego, utilizando tecnologías modernas de backend (Flask, PostgreSQL) y frontend (Unity).

### Objetivos Específicos

- ✅ Diseñar una **API RESTful en Flask** que exponga operaciones CRUD sobre puntuaciones
- ✅ Implementar una base de datos **PostgreSQL** robusta y normalizada
- ✅ Desarrollar un cliente interactivo en **Unity** con C#
- ✅ Garantizar **seguridad de datos** mediante JWT y CORS
- ✅ Crear un sistema de **privacidad y amistades** flexible
- ✅ Implementar **autenticación robusta** con recuperación de contraseña
- ✅ Generar **informes automáticos** con JasperReports
- ✅ Asegurar **escalabilidad y mantenibilidad** del código

---

## 🛠️ Tecnologías Utilizadas

### Backend

| Tecnología | Versión | Descripción |
|---|---|---|
| **Python** | 3.9+ | Lenguaje de programación principal |
| **Flask** | 3.0.3 | Framework web ligero y flexible |
| **Flask-SQLAlchemy** | 3.1.1 | ORM para manejo de base de datos |
| **Flask-Cors** | 5.0.0 | Soporte para Cross-Origin Resource Sharing |
| **Flask-Mail** | 0.10.0 | Servicio de correo electrónico |
| **PyJWT** | 2.10.1 | Autenticación con JSON Web Tokens |
| **psycopg2** | 2.9.9 | Driver PostgreSQL |

### Frontend

| Tecnología | Descripción |
|---|---|
| **Unity** | Motor de videojuegos |
| **C#** | Lenguaje de programación |
| **SimpleJSON** | Parsing de JSON en Unity |
| **UnityWebRequest** | HTTP requests desde Unity |

### Base de Datos

| Tecnología | Descripción |
|---|---|
| **PostgreSQL** | Sistema de gestión de base de datos relacional |
| **SQL** | Lenguaje de consultas |

### Generación de Informes

| Tecnología | Descripción |
|---|---|
| **Java** | Lenguaje para generador de reportes |
| **JasperReports** | Framework de generación de informes PDF |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE UNITY (Frontend)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ • Pantalla de Login/Registro                         │   │
│  │ • Leaderboard (ordenar, filtrar, paginar)           │   │
│  │ • Gestión de Perfil (actualizar datos)              │   │
│  │ • Sistema de Amigos (enviar, aceptar, rechazar)     │   │
│  │ • Control de Privacidad (público/privado/amigos)    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON (UnityWebRequest)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│              API REST FLASK (Backend - Python)               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ • Autenticación (JWT)                               │    │
│  │ • Gestión de Usuarios (/jugadores/*)                │    │
│  │ • Gestión de Puntuaciones (/puntuaciones/*)          │    │
│  │ • Gestión de Privacidad (/privacidad/*)             │    │
│  │ • Sistema de Amistades (/amistades/*)               │    │
│  │ • Recuperación de Contraseña (con mail)             │    │
│  │ • CORS configurado para seguridad                   │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────┬─────────────────────────────────┘
                           │ SQL Queries (SQLAlchemy)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│         BASE DE DATOS PostgreSQL (Persistencia)              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Tabla: jugadores      (usuarios registrados)        │    │
│  │ Tabla: puntuaciones   (scores de jugadores)         │    │
│  │ Tabla: privacidad     (configuración privacidad)    │    │
│  │ Tabla: amistades      (relaciones entre usuarios)   │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘

                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│       GENERADOR DE INFORMES (Java + JasperReports)          │
│  • Informe de Jugadores (datos personales)                  │
│  • Informe de Puntuaciones (ranking y scores)               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📦 Requisitos e Instalación

### Requisitos del Sistema

- **Python:** 3.9 o superior
- **PostgreSQL:** 12 o superior
- **Unity:** 2020.3 LTS o superior
- **Java:** 11 o superior (para generación de informes)
- **Node.js/npm:** (opcional, para herramientas de desarrollo)

### Instalación del Backend

#### 1. Clonar el repositorio

```bash
git clone https://github.com/Juanito-Software/Sistema-Leaderboard-DAM.git
cd Sistema-Leaderboard-DAM/backend
```

#### 2. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# Database
DATABASE_URL=postgresql://client:<contraseña>@localhost:5432/game

# JWT
SECRET_KEY=<generar con: python -c "import secrets; print(secrets.token_urlsafe(48))">
JWT_EXPIRATION_HOURS=1

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=deadvalleygame@gmail.com
MAIL_PASSWORD=mwig lnax nfpm dwjg

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://misitio.com
```

#### 5. Configurar PostgreSQL

```bash
# Conectar a PostgreSQL
psql -U postgres

# Ejecutar script de inicialización
\i postgres.sql

# Verificar usuario 'client' creado
\du
```

#### 6. Crear tablas (primera ejecución)

```bash
python
>>> from app import app, db
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

#### 7. Ejecutar API

```bash
python app.py
# o con Gunicorn (producción)
gunicorn -w 4 app:app
```

La API estará disponible en `http://localhost:5000`

### Instalación del Frontend (Unity)

#### 1. Abrir proyecto en Unity

```bash
# Opción 1: Desde Unity Hub
- Abrir Unity Hub
- Seleccionar "Open" → ruta al proyecto

# Opción 2: Línea de comandos
unity -projectPath ./Frontend-Unity
```

#### 2. Importar paquetes necesarios

```
Assets → Import Package → SimpleJSON (si no está incluido)
```

#### 3. Configurar conexión a API

En `Assets/Scripts/Controllers/LeaderBoardApi.cs`:

```csharp
private string apiUrl = "http://localhost:5000/puntuaciones";
```

#### 4. Ejecutar en Editor

Presionar **Play** en el editor de Unity.

### Instalación de Generador de Reportes

```bash
cd informes/JasperReportExecutor
mvn clean install
```

---

## ⚙️ Configuración

### Configuración de PostgreSQL (pg_hba.conf)

Ubicación: `C:\Program Files\PostgreSQL\17\data\pg_hba.conf`

```
# IPv4 local connections:
host    all             admin           127.0.0.1/32            password
host    game            client          127.0.0.1/32            password
host    all             all             127.0.0.1/32            reject
```

### Configuración de CORS en Flask

Archivo: `config.py`

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # Desarrollo local
    'https://misitio.com',        # Producción
]
CORS_SUPPORTS_CREDENTIALS = True
CORS_HEADERS = 'Content-Type', 'Authorization'
```

### Configuración de JWT

Token válido por **1 hora**. Para cambiar:

```python
# app.py
expiration_time = datetime.now(timezone.utc) + timedelta(hours=2)
```

---

## 📁 Estructura del Proyecto

```
Sistema-Leaderboard-DAM/
│
├── backend/                          # API Flask
│   ├── app.py                        # Punto de entrada principal
│   ├── models.py                     # Modelos de base de datos (SQLAlchemy)
│   ├── config.py                     # Configuración (BD, JWT, CORS)
│   ├── requirements.txt              # Dependencias Python
│   ├── postgres.sql                  # Script de inicialización BD
│   └── migrations/                   # Migraciones de BD (Alembic)
│
├── frontend/                         # Cliente Unity
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── Controllers/
│   │   │   │   ├── AuthController.cs
│   │   │   │   ├── LeaderBoardApi.cs
│   │   │   │   ├── FriendsController.cs
│   │   │   │   └── ProfileController.cs
│   │   │   ├── UI/
│   │   │   │   ├── LeaderboardUI.cs
│   │   │   │   ├── FriendsUI.cs
│   │   │   │   └── ProfileUI.cs
│   │   │   └── Models/
│   │   │       ├── Jugador.cs
│   │   │       └── Puntuacion.cs
│   │   └── Scenes/
│   │       ├── LoginScene
│   │       ├── MenuScene
│   │       ├── LeaderboardScene
│   │       └── ProfileScene
│   └── ProjectSettings/
│
├── informes/                         # Generador JasperReports
│   └── JasperReportExecutor/
│       ├── pom.xml
│       ├── src/
│       │   └── JasperReportExecutor.java
│       └── resources/
│           ├── informePuntuaciones.jasper
│           └── informeJugadores.jasper
│
├── documentacion/                    # Documentación del proyecto
│   ├── TFG_Sistema_Leaderboard.pdf
│   ├── Diagramas_Arquitectura.pdf
│   └── Manual_Usuario.pdf
│
└── README.md                         # Este archivo
```

---

## ▶️ Uso y Ejecución

### Ejecución Completa del Sistema

#### Paso 1: Iniciar PostgreSQL

```bash
# Windows
pg_ctl -D "C:\Program Files\PostgreSQL\17\data" start

# Linux
sudo systemctl start postgresql

# macOS
brew services start postgresql
```

#### Paso 2: Ejecutar Script de Base de Datos

```bash
psql -U postgres -f postgres.sql
```

#### Paso 3: Iniciar API Flask

```bash
cd backend
python app.py
# API disponible en http://localhost:5000
```

#### Paso 4: Ejecutar Cliente Unity

```bash
# Opción 1: Editor de Unity
unity -projectPath ./frontend

# Opción 2: Build compilado
./Builds/Dead Valley.exe
```

#### Paso 5: Generar Reportes (Opcional)

```bash
cd informes/JasperReportExecutor/target
java -jar JasperReportExecutor-1.0-SNAPSHOT.jar
# Genera: informePuntuaciones.pdf, informeJugadores.pdf
```

### Flujo Típico de Usuario

```
1. INICIO DE SESIÓN
   └─ Pantalla Login → Credenciales → Autenticación JWT → Token almacenado

2. MENÚ PRINCIPAL
   ├─ JUGAR
   │  └─ Completar partida → POST /puntuaciones → Puntuación registrada
   ├─ LEADERBOARD
   │  ├─ GET /puntuaciones → Ver ranking
   │  ├─ Filtrar por nombre → GET /puntuaciones/{nombre}
   │  └─ Ordenar asc/desc → GET /puntuaciones?order=asc
   ├─ PERFIL
   │  ├─ GET /jugadores/perfil → Ver datos
   │  ├─ PUT /jugadores/perfil → Actualizar datos
   │  └─ PUT /privacidad/{id} → Cambiar nivel privacidad
   └─ AMIGOS
      ├─ POST /amistades/enviar_solicitud → Enviar solicitud
      ├─ GET /amistades/obtener_pendientes → Ver solicitudes
      ├─ POST /amistades/aceptar_solicitud → Aceptar amistad
      └─ GET /amistades/obtener_amigos → Ver lista amigos

3. CIERRE DE SESIÓN
   └─ Eliminar token local
```

---

## ✨ Funcionalidades Principales

### 1. Autenticación y Registro

- ✅ Registro de nuevos jugadores
- ✅ Login con credenciales
- ✅ Recuperación de contraseña por email
- ✅ Tokens JWT seguros
- ✅ Roles de usuario (jugador/admin)

### 2. Gestión de Puntuaciones

- ✅ Envío automático de puntuaciones al terminar partida
- ✅ Solo se guarda la puntuación más alta
- ✅ Leaderboard global ordenable (asc/desc)
- ✅ Búsqueda de puntuaciones por nombre de jugador
- ✅ Paginación de resultados (15 registros por página)

### 3. Sistema de Privacidad

- ✅ Tres niveles: **público**, **privado**, **solo amigos**
- ✅ Control granular de visibilidad de puntuaciones
- ✅ Verificación automática de amistades para acceso

### 4. Gestión de Amigos

- ✅ Envío de solicitudes de amistad
- ✅ Aceptar/rechazar solicitudes
- ✅ Lista de amigos aceptados
- ✅ Vista de solicitudes pendientes
- ✅ Relación bidireccional de amistades

### 5. Gestión de Perfil

- ✅ Visualización de datos personales
- ✅ Edición de nombre, email, teléfono
- ✅ Cambio de nivel de privacidad
- ✅ Validación de datos en tiempo real

### 6. Generación de Informes

- ✅ Informe de jugadores (datos personales)
- ✅ Informe de puntuaciones (rankings)
- ✅ Exportación a PDF
- ✅ Acceso solo para administradores

### 7. Administración

- ✅ Eliminación de puntuaciones individuales
- ✅ Limpieza de todas las puntuaciones
- ✅ Limpieza de todos los jugadores
- ✅ Acceso solo con rol admin + token JWT

---

## 🗄️ Base de Datos

### Diagrama Entidad-Relación

```
┌──────────────────────────────┐
│       JUGADORES              │
├──────────────────────────────┤
│ id (PK)                      │ ◄─┐
│ nombre (UNIQUE)              │   │
│ email (UNIQUE)               │   │
│ numtelefono (UNIQUE)         │   │
│ password (HASH)              │   │ 1:1
│ rol (DEFAULT 'jugador')      │   │
│ refresh_token                │   │
└──────────────────────────────┘   │
     │                             │
     │ 1:1                         │
     ▼                             │
┌──────────────────────────────┐   │
│    PUNTUACIONES              │   │
├──────────────────────────────┤   │
│ id (PK)                      │   │
│ valor (INT)                  │   │
│ jugador_id (FK, UNIQUE) ─────┼───┘
└──────────────────────────────┘
     
     1:1
     │
     ▼
┌──────────────────────────────┐
│     PRIVACIDAD               │
├──────────────────────────────┤
│ id (PK)                      │
│ nivel_de_privacidad (ENUM)   │
│ jugador_id (FK) ─────────────┼─┐
└──────────────────────────────┘ │
                                  │
                            ┌─────┴────────────────┐
                            │                      │
                    ┌───────▼─────────┐   ┌───────▼─────────┐
                    │   AMISTADES     │   │  JUGADORES (2)  │
                    ├─────────────────┤   └─────────────────┘
                    │ id (PK)         │
                    │ jugador_        │
                    │  solicitante_id │ ◄─ 1:N
                    │ jugador_        │
                    │  receptor_id    │ ◄─ 1:N
                    │ estado (DEFAULT │
                    │  'pendiente')   │
                    └─────────────────┘
```

### Tablas Principales

#### JUGADORES
| Campo | Tipo | Restricciones |
|-------|------|---|
| id | SERIAL | PRIMARY KEY |
| nombre | VARCHAR(12) | UNIQUE, NOT NULL |
| email | VARCHAR(50) | UNIQUE |
| numtelefono | VARCHAR(9) | UNIQUE |
| password | VARCHAR(256) | NOT NULL |
| rol | VARCHAR(20) | DEFAULT 'jugador' |
| refresh_token | VARCHAR(255) | (futuro) |

#### PUNTUACIONES
| Campo | Tipo | Restricciones |
|-------|------|---|
| id | SERIAL | PRIMARY KEY |
| valor | INTEGER | NOT NULL |
| jugador_id | INTEGER | FK → jugadores.id, UNIQUE |

#### PRIVACIDAD
| Campo | Tipo | Restricciones |
|-------|------|---|
| id | SERIAL | PRIMARY KEY |
| nivel_de_privacidad | ENUM | ('publico', 'privado', 'amigos'), DEFAULT 'publico' |
| jugador_id | INTEGER | FK → jugadores.id |

#### AMISTADES
| Campo | Tipo | Restricciones |
|-------|------|---|
| id | SERIAL | PRIMARY KEY |
| jugador_solicitante_id | INTEGER | FK → jugadores.id |
| jugador_receptor_id | INTEGER | FK → jugadores.id |
| estado | VARCHAR(20) | DEFAULT 'pendiente' |

### Normalización

✅ **1FN (Primera Forma Normal):** Todos los atributos son atómicos  
✅ **2FN (Segunda Forma Normal):** Todos los atributos dependen completamente de la clave primaria  
✅ **3FN (Tercera Forma Normal):** No hay dependencias transitivas  

---

## 🔌 API REST Endpoints

### Autenticación

#### Registro de Usuario
```http
POST /jugadores/register
Content-Type: application/json

{
  "nombre": "jugador1",
  "password": "pass123",
  "email": "jugador1@gmail.com",
  "numtelefono": "638703516"
}

Respuesta 201:
{
  "id": 1,
  "nombre": "jugador1"
}
```

#### Login
```http
POST /jugadores/login
Content-Type: application/json

{
  "nombre": "jugador1",
  "password": "pass123"
}

Respuesta 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### Recuperar Contraseña
```http
POST /jugadores/send-reset-email
Content-Type: application/json

{
  "email": "jugador1@gmail.com"
}

Respuesta 200:
{
  "message": "Correo enviado exitosamente"
}
```

#### Restablecer Contraseña
```http
POST /jugadores/reset-password/<reset_token>
Content-Type: application/x-www-form-urlencoded

password=newpass123&repeatpassword=newpass123

Respuesta 200: Página HTML con confirmación
```

### Puntuaciones

#### Obtener Leaderboard Global
```http
GET /puntuaciones?order_by=valor&order=desc&page=1&per_page=15
Authorization: Bearer <access_token>

Respuesta 200:
{
  "puntuaciones": [
    {
      "id": 1,
      "valor": 99,
      "jugador": {
        "id": 4,
        "nombre": "jugador1"
      }
    }
  ],
  "total_pages": 5,
  "current_page": 1
}
```

#### Obtener Puntuación por Jugador
```http
GET /puntuaciones/jugador1?page=1&per_page=15
Authorization: Bearer <access_token>

Respuesta 200: (Similar al anterior, filtrado por nombre)
```

#### Enviar/Actualizar Puntuación
```http
POST /puntuaciones
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "nombre": "jugador1",
  "valor": 150
}

Respuesta 201 (nueva): Puntuación creada
Respuesta 200 (actualizada): Si 150 > puntuación anterior
Respuesta 422: Si 150 ≤ puntuación anterior
```

#### Eliminar Puntuación (Admin)
```http
DELETE /puntuaciones/jugador1
Authorization: Bearer <access_token>

Respuesta 200: Puntuación eliminada
Respuesta 403: Sin permisos admin
```

#### Limpiar Todas Puntuaciones (Admin)
```http
DELETE /puntuaciones/limpiar
Authorization: Bearer <access_token>

Respuesta 200: Todas eliminadas
```

### Perfil de Usuario

#### Obtener Perfil
```http
GET /jugadores/perfil
Authorization: Bearer <access_token>

Respuesta 200:
{
  "id": 4,
  "nombre": "jugador1",
  "email": "jugador1@gmail.com",
  "numtelefono": "638703516"
}
```

#### Actualizar Perfil
```http
PUT /jugadores/perfil
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "nombre": "jugador_nuevo",
  "email": "nuevo@gmail.com",
  "numtelefono": "638703517"
}

Respuesta 200: Perfil actualizado
```

### Privacidad

#### Obtener Nivel de Privacidad
```http
GET /privacidad/4
Authorization: Bearer <access_token>

Respuesta 200:
{
  "jugador_id": 4,
  "nivel_de_privacidad": "publico"
}
```

#### Actualizar Privacidad
```http
PUT /privacidad/4
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "nivel_de_privacidad": "amigos"
}

Respuesta 200: Privacidad actualizada
```

### Amistades

#### Enviar Solicitud de Amistad
```http
POST /amistades/enviar_solicitud
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "nombre_receptor": "jugador2"
}

Respuesta 201: Solicitud enviada
```

#### Obtener Solicitudes Pendientes
```http
GET /amistades/obtener_pendientes
Authorization: Bearer <access_token>

Respuesta 200:
{
  "pendientes": [
    {
      "nombre": "jugador3",
      "solicitante_id": 5,
      "receptor_id": 4
    }
  ]
}
```

#### Aceptar Solicitud
```http
POST /amistades/aceptar_solicitud
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "solicitante_id": 5,
  "receptor_id": 4
}

Respuesta 200: Solicitud aceptada
```

#### Rechazar Solicitud
```http
POST /amistades/rechazar_solicitud
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "solicitante_id": 5,
  "receptor_id": 4
}

Respuesta 200: Solicitud rechazada
```

#### Obtener Lista de Amigos
```http
GET /amistades/obtener_amigos
Authorization: Bearer <access_token>

Respuesta 200:
{
  "amigos": [
    {
      "id": 5,
      "nombre": "jugador2"
    }
  ]
}
```

---

## 🔐 Seguridad

### Implementaciones de Seguridad

#### 1. **Autenticación JWT**
- Tokens con expiración de 1 hora
- Algoritmo HS256
- Token obligatorio en header `Authorization: Bearer <token>`
- Validación en rutas protegidas

```python
@app.route('/ruta-protegida', methods=['GET'])
@authenticate_token
def ruta_protegida():
    return jsonify({'message': 'Acceso permitido'})
```

#### 2. **Cifrado de Contraseñas**
- Uso de `werkzeug.security.generate_password_hash`
- Hashing seguro con salt automático
- Nunca se almacenan contraseñas en texto plano

```python
from werkzeug.security import generate_password_hash, check_password_hash

password_hash = generate_password_hash('password123')
check_password_hash(password_hash, 'password123')  # True
```

#### 3. **CORS (Cross-Origin Resource Sharing)**
- Solo dominios permitidos pueden acceder a la API
- Validación en `config.py`

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://misitio.com'
]
```

#### 4. **Control de Acceso (RBAC)**
- Rol **'jugador'** (por defecto): acceso a endpoints estándar
- Rol **'admin'** (manual en BD): acceso a operaciones sensibles

```python
@app.route('/puntuaciones/limpiar', methods=['DELETE'])
@authenticate_token2(required_role="admin")
def limpiar_puntuaciones():
    # Solo admins pueden acceder
```

#### 5. **Validación de Datos de Entrada**
- Validación de tipos en endpoints
- Mensajes de error descriptivos
- Prevención de inyección SQL (SQLAlchemy ORM)

#### 6. **Privacidad de Datos**
- Verificación de niveles de privacidad en leaderboard
- Solo amigos pueden ver puntuaciones "privadas"
- Relación de amistad verificada antes de acceso

#### 7. **HTTPS (Futuro)**
- Recomendación: configurar SSL/TLS en producción
- Certificados Let's Encrypt gratuitos

### Guía de Seguridad para Desarrolladores

```python
# ✅ SEGURO: Usar SQLAlchemy ORM
usuario = Jugadores.query.filter_by(id=user_id).first()

# ❌ INSEGURO: Concatenación manual
db.session.execute(f"SELECT * FROM jugadores WHERE id = {user_id}")

# ✅ SEGURO: Usar parámetros
db.session.execute(
    text("SELECT * FROM jugadores WHERE id = :user_id"),
    {"user_id": user_id}
)
```

---

## 🚀 Despliegue

### Despliegue en Producción

#### Opción 1: Gunicorn + Nginx

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Configuración Nginx (/etc/nginx/sites-available/leaderboard)
server {
    listen 80;
    server_name leaderboard.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Opción 2: Heroku

```bash
# Instalar Heroku CLI
heroku login

# Crear aplicación
heroku create mi-leaderboard

# Configurar variables de entorno
heroku config:set DATABASE_URL=postgresql://...
heroku config:set SECRET_KEY=...

# Desplegar
git push heroku main
```

#### Opción 3: AWS / Google Cloud / Azure

Consultar documentación específica de cada proveedor.

### Configuración de IP Pública

Si no tienes IP pública, opciones alternativas:

1. **ngrok** (tunneling temporal)
   ```bash
   ngrok http 5000
   ```

2. **Servicios de hosting** (AWS, Heroku, DigitalOcean)

3. **Contratar IP estática** con tu ISP

### Base de Datos en Producción

- Backup regular con `pg_dump`
- Replicación de BD para alta disponibilidad
- Monitoreo con herramientas (Prometheus, New Relic)
- Logs centralizados (ELK Stack)

---

## 🐛 Troubleshooting

| Problema | Causa | Solución |
|---------|-------|----------|
| `"No module named 'flask'"` | Dependencias no instaladas | `pip install -r requirements.txt` |
| `"Connection refused to PostgreSQL"` | PostgreSQL no iniciado | `pg_ctl start -D <ruta_datos>` |
| `"Permission denied" (admin)` | Token inválido o sin rol admin | Verificar rol en BD: `UPDATE jugadores SET rol='admin' WHERE id=X` |
| `"CORS error"` | Origen no permitido | Añadir a `CORS_ALLOWED_ORIGINS` |
| `"Token expired"` | JWT expirado (>1 hora) | Usuario debe loguearse de nuevo |
| `"Contraseña no coincide"` | Error en recuperación de contraseña | Verificar email y token válido |
| `"Column does not exist"` | Migraciones pendientes | Ejecutar `postgres.sql` completo |
| `"Endpoint not found"` | URL incorrecta o typo | Verificar endpoint en documentación |

---

## 🔮 Contribuciones Futuras

### Corto Plazo (Próximos Meses)

- [ ] **Refresh Tokens:** Renovación automática de sesiones
- [ ] **Notificaciones Real-time:** WebSockets para eventos en vivo
- [ ] **Mobile Responsivo:** Adaptación completa a dispositivos móviles
- [ ] **Mejorar UI/UX:** Animaciones y transiciones
- [ ] **Testing Automático:** Unit tests y tests de integración
- [ ] **Documentación API:** Swagger/OpenAPI

### Mediano Plazo

- [ ] **Soporte HTTPS/SSL:** Seguridad en tránsito
- [ ] **Caché Redis:** Optimización de rendimiento
- [ ] **Estadísticas Avanzadas:** Gráficos de progreso
- [ ] **Logros/Trofeos:** Sistema de gamificación
- [ ] **Torneos:** Competiciones por temporadas
- [ ] **Chat Multiplayer:** Sistema de mensajería

### Largo Plazo

- [ ] **App Mobile Nativa:** iOS y Android
- [ ] **Replicas BD:** Alta disponibilidad
- [ ] **Microservicios:** Descomposición de la API
- [ ] **Analytics:** Seguimiento de usuario
- [ ] **IA/Recomendaciones:** Sugerencias inteligentes
- [ ] **Monetización:** Sistema de pagos (Stripe)

---

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**.

Eres libre de:
- ✅ Usar el código
- ✅ Modificar el código
- ✅ Distribuir el código
- ❌ Pero DEBES mantener la licencia GPLv3

Para más detalles: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

---

## 📧 Contacto

**Juan Bernáldez Pereda**  
📧 Email: [bernaldezperedaj@gmail.com](mailto:bernaldezperedaj@gmail.com)  
🐙 GitHub: [@Juanito-Software](https://github.com/Juanito-Software)  
💼 LinkedIn: [Juan Bernáldez Pereda](https://linkedin.com/in/juanbernaldezpereda)  

---

## 📚 Recursos Adicionales

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Unity Manual](https://docs.unity3d.com/)
- [JWT RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519)
- [REST API Best Practices](https://restfulapi.net/)
- [OWASP Security Guidelines](https://owasp.org/)

---

## 🎓 Información Académica

**Proyecto de Fin de Grado (TFG)**  
**Ciclo Formativo:** Desarrollo de Aplicaciones Multiplataforma (DAM)  
**Curso Académico:** 2024/2025  
**Institución:** [Centro de Formación]  
**Tutor:** [Nombre del Tutor]  
**Fecha de Presentación:** 28 de Septiembre de 2024  

---

**Última actualización:** Enero 2025  
**Estado del Proyecto:** ✅ Completado (v1.0)  
**Mantenimiento:** Activo

