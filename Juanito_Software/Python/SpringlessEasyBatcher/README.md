# ⚡ SpringlessEasyBatcher — Suite de Procesamiento por Lotes sin Spring

**Autor:** JuanitoSoftware · **Versión:** 1.0 · **Licencia:** GNU GPL v3 · **Lenguaje:** Python 3

---

## 🧾 Descripción

Suite completa de **procesamiento de datos en lote (batch)** con un **módulo core genérico y reutilizable** (`batch_processor.py`) y una **aplicación REST de ejemplo** (`flask_api_personas.py`). Diseñada como alternativa ligera a Spring Batch, sin necesitar Java ni infraestructura pesada.

Procesa datos masivamente desde múltiples fuentes (CSV, API, base de datos) hacia múltiples destinos, aplicando transformaciones intermedias mediante un **pipeline configurable interactivamente**.

---

## 🚀 Características

### 🔄 Núcleo Genérico (batch_processor.py)
- **Pipeline reutilizable**: procesa cualquier clase `@dataclass` de forma modular
- **Entrada versátil**: CSV, API REST o base de datos (PostgreSQL, MySQL, SQL Server, SQLite)
- **Salida flexible**: CSV, API REST o base de datos
- **Conversión automática**: transformación entre `pandas.DataFrame` y objetos Python
- **Orquestador interactivo**: configura el flujo completo desde la terminal
- **Funciones transformadoras**: encadena pasos de procesamiento fácilmente
- **Extensible**: añade nuevas fuentes, destinos o pasos de procesamiento

### 🌐 Aplicación REST de Ejemplo (flask_api_personas.py)
- **API REST con Flask**: endpoints HTTP para disparar y controlar el batch
- **Ingesta desde CSV**: lee `input_personas.csv` e inserta en base de datos SQL
- **Dataclasses tipadas**: modelos de datos limpios y seguros
- **Base de datos de ejemplo**: script SQL (`Levantar_Personas.sql`) incluido
- **Lanzamiento automático**: script `.bat` para Windows
- **Documentación paso a paso**: `Instrucciones_de_uso.txt`

---

## ⚙️ Requisitos del Sistema

- **Python:** 3.9 o superior
- **Base de datos SQL** (opcional, solo si usas como destino/origen):
  - SQL Server, PostgreSQL, MySQL, SQLite, etc.

### Dependencias Python

```bash
# Núcleo genérico (batch_processor.py):
pip install pandas requests sqlalchemy

# Para PostgreSQL:
pip install psycopg2

# Para MySQL:
pip install mysql-connector-python

# Para SQL Server (recomendado):
pip install pyodbc

# Aplicación REST de ejemplo:
pip install flask
```

---

## 📦 Instalación

```bash
cd SpringlessEasyBatcher
pip install pandas requests sqlalchemy flask pyodbc
```

Configura la cadena de conexión a la base de datos en `flask_api_personas.py`:

```python
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=mi_base_datos;"
    "UID=usuario;"
    "PWD=contraseña"
)
```

---

## 📁 Estructura del Proyecto

```plaintext
SpringlessEasyBatcher/
├── batch_processor.py           # Módulo core reutilizable
├── flask_api_personas.py        # Aplicación REST de ejemplo
├── dataclass_template.py        # Template de clase @dataclass
├── Levantar_Personas.sql        # Script SQL de ejemplo
├── input_personas.csv           # Datos de entrada de ejemplo
├── output_personas.csv          # Datos de salida (generado)
├── Instrucciones_de_uso.txt     # Guía paso a paso
├── run_api_personas.bat         # Lanzador rápido (Windows)
└── Licencia/
    └── LICENSE.txt
```

---

## 💻 Uso: Dos Perspectivas

### 📌 Opción 1: Usar el Módulo Core Genérico (batch_processor.py)

Para procesar **cualquier clase de datos** con un pipeline flexible:

#### Paso 1: Definir tu clase de entidad

```python
from dataclasses import dataclass

@dataclass
class Persona:
    id: int
    first_name: str
    last_name: str
    email: str
```

#### Paso 2: Ejecutar el orquestador interactivo

```bash
python batch_processor.py
```

#### Paso 3: Responder las preguntas en consola

```
¿Ruta de tu clase @dataclass? → /ruta/a/dataclass_template.py
¿Nombre de tu clase? → Persona
¿Tipo de entrada (csv/api/db)? → csv
¿Ruta de entrada? → ./input_personas.csv
¿Tipo de salida (csv/api/db)? → db
¿Ruta de salida (connection_string)? → postgresql://user:pass@localhost/bd_destino
¿Nombre de tabla? → personas
```

El pipeline se ejecuta automáticamente con las transformaciones configuradas.

#### Personalizar el Pipeline

```python
from batch_processor import Processor

proc = Processor[Persona]()
proc.add(strip_whitespace)      # Función personalizada
proc.add(to_uppercase_names)    # Tu transformación
proc.add(validate_emails)       # Validación custom
```

---

### 🌐 Opción 2: Usar la API REST de Ejemplo (flask_api_personas.py)

Para procesar datos masivamente desde **cualquier cliente HTTP**:

#### Paso 1: Preparar la base de datos

Ejecuta el script SQL:

```sql
-- Crea la tabla de destino
-- Archivo: Levantar_Personas.sql
```

#### Paso 2: Preparar los datos de entrada

Edita `input_personas.csv`:

```csv
id,nombre,apellido,email
1,Juan,Pérez,juan@example.com
2,María,González,maria@example.com
...
```

#### Paso 3: Levantar la API

**Windows (automático):**
```bash
Doble clic en run_api_personas.bat
```

**Consola (todos los sistemas):**
```bash
python flask_api_personas.py
```

La API estará disponible en `http://localhost:5000`

#### Paso 4: Disparar el batch

```bash
# Con curl:
curl -X POST http://localhost:5000/batch/run

# Con Python:
import requests
requests.post("http://localhost:5000/batch/run")

# Con PowerShell:
Invoke-WebRequest -Uri "http://localhost:5000/batch/run" -Method POST
```

#### Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/batch/run` | Inicia la carga masiva desde CSV a BD |
| GET | `/batch/status` | Obtiene el estado del último batch |
| GET | `/health` | Verifica que la API está activa |

---

## 🔧 Pasos de Procesamiento (Pipeline)

El núcleo sigue este flujo automáticamente:

```
1. LECTURA
   ├─ CSV → pandas.DataFrame
   ├─ API REST → JSON → pandas.DataFrame
   └─ Base de datos → Rows → pandas.DataFrame

2. CONVERSIÓN
   └─ DataFrame → Objetos @dataclass

3. PROCESAMIENTO
   ├─ strip_whitespace (elimina espacios)
   ├─ validate_data (valida campos)
   ├─ Tus funciones personalizadas...
   └─ Aplicar pipeline configurado

4. SALIDA
   ├─ Objetos → CSV
   ├─ Objetos → POST a API REST
   └─ Objetos → INSERT en base de datos
```

---

## 🧩 Personalización

### Ejemplo: Añadir transformación personalizada

```python
def to_uppercase_names(persona: Persona) -> Persona:
    persona.first_name = persona.first_name.upper()
    persona.last_name = persona.last_name.upper()
    return persona

# Usar en pipeline:
processor.add(to_uppercase_names)
```

### Ejemplo: Validar datos

```python
def validate_email(persona: Persona) -> Persona:
    if "@" not in persona.email:
        raise ValueError(f"Email inválido: {persona.email}")
    return persona
```

### Ejemplo: Conexión a base de datos personalizada

Modifica la cadena de conexión SQLAlchemy según tu BD:

```python
# PostgreSQL
"postgresql://user:password@localhost/dbname"

# MySQL
"mysql+pymysql://user:password@localhost/dbname"

# SQL Server
"mssql+pyodbc://user:password@server/dbname?driver=ODBC+Driver+17+for+SQL+Server"

# SQLite
"sqlite:///./database.db"
```

---

## 📊 Casos de Uso

1. **Migración de datos**: transferir datos entre bases de datos heterogéneas
2. **Sincronización**: sincronizar datos entre sistemas
3. **ETL ligero**: extrae, transforma y carga datos sin herramientas pesadas
4. **Validación masiva**: procesa y valida millones de registros
5. **Transformación de formatos**: CSV → JSON → BD, etc.
6. **Integración de APIs**: ingesta datos de APIs externas

---

## 🔮 Próximos Pasos

- **Validación automática**: integración con `pydantic` para esquemas robustos
- **Interfaz gráfica**: GUI con `Tkinter` o `PyQt` para usuarios no técnicos
- **Logging estructurado**: registros detallados en lugar de `print`
- **CLI avanzada**: herramienta de línea de comandos con `argparse` o `Typer`
- **Monitoreo**: dashboard de métricas de batch (duración, registros procesados, errores)
- **Reintentos y recuperación**: manejo de fallos con reintentos automáticos
- **Procesamiento paralelo**: multithread/multiprocess para grandes volúmenes

---

## ⚖️ Licencia

Este programa es software libre: puedes redistribuirlo y/o modificarlo bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)** o cualquier versión posterior.

Más información: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

© 2025 JuanitoSoftware

---

## 📬 Contacto

📧 bernaldezperedaj@gmail.com
