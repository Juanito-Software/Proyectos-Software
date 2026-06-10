Aquí tienes el `README.md` definitivo y unificado para **SpringlessEasyBatcher**. Se han consolidado las dos vertientes del proyecto: el núcleo procesador ETL basado en consolas interactivas u objetos tipados (`dataclass`) y la arquitectura de API distribuida en Flask para la ingesta y automatización mediante disparadores HTTP.

---

# 🔁 SpringlessEasyBatcher - Batching Masivo y Pipelines ETL sin Spring

**Versión:** 1.0

**Desarrollado por:** Juanito Software

**Licencia:** [GNU GPLv3 / Uso No Comercial Personal](https://www.gnu.org/licenses/gpl-3.0.html) (Ver sección de Licencia)

---

## 📄 Descripción

**SpringlessEasyBatcher** es un ecosistema y framework ágil en Python diseñado para el procesamiento de datos en lote (*batch*), migraciones masivas e integraciones ETL livianas. Nace como una alternativa ligera, modular y rápida a la robusta infraestructura de *Spring Batch* (Java), eliminando la necesidad de servidores pesados.

El proyecto consta de dos aproximaciones unificadas:

1. **Un núcleo ETL genérico (`batch_processor.py`)**: Capaz de orquestar flujos interactivamente desde consola uniendo múltiples orígenes (CSV, API, DB) con destinos equivalentes, utilizando objetos tipados nativos de Python (`@dataclass`).
2. **Una API de control distribuido (`flask_api_personas.py`)**: Un servicio web basado en Flask que expone endpoints HTTP para disparar, automatizar y controlar procesos de ingesta masiva de datos en segundo plano.

---

## 🚀 Características Principales

* 🔄 **Pipeline Genérico y Modular**: Define pasos intermedios de transformación de datos de tipo $T \rightarrow T$ (ej. limpieza de espacios, conversión a mayúsculas) de forma desacoplada.
* 🔌 **Entrada y Salida Polimórfica**: Capacidad nativa para leer y escribir de manera cruzada entre archivos planos (CSV), APIs REST y Bases de Datos Relacionales mediante SQLAlchemy u ODBC.
* 🧠 **Conversión Automática de Tipos**: Mapeo transparente e inteligente entre estructuras bidimensionales de `pandas.DataFrame` y las `@dataclass` fuertemente tipadas de Python.
* ⚡ **Disparadores HTTP**: Endpoints REST con Flask para integrarse con herramientas de automatización o tareas programadas (*cron jobs*) remotas.
* 🎛️ **Orquestador Interactivo**: Incluye un asistente por consola (`SpringlessEasyBatch.exe`) para configurar dinámicamente un pipeline de datos sin necesidad de picar código.
* 🚀 **Despliegue Rápido**: Scripts de automatización en Windows (`.bat`) para levantar los servicios locales con un solo clic.

---

## 🗃️ Estructura del Proyecto Recomendada

```text
📁 SpringlessEasyBatcher/
│
├── SpringlessEasyBatch.exe    # Asistente interactivo compilado para Windows
├── batch_processor.py         # Núcleo modular del procesador genérico (ETL)
├── flask_api_personas.py      # API REST en Flask para control de disparos batch
├── run_api_personas.bat       # Script automatizado para arrancar la API en Windows
├── dataclass_template.py      # Plantilla base para la definición de tus entidades
│
├── 📁 Datos_y_Scripts/
│   ├── input_personas.csv     # Archivo CSV de datos de entrada de ejemplo
│   ├── output_personas.csv    # Archivo CSV generado como salida de ejemplo
│   └── Levantar_Personas.sql  # Script SQL para estructurar las tablas de pruebas
│
└── 📋 Documentación/
    ├── Instrucciones_de_uso.txt  # Guía manual paso a paso del flujo completo
    └── LICENSE.txt               # Documento de términos de licenciamiento

```

---

## 🛠️ Requisitos del Sistema

* **Python 3.9 o superior**
* **Base de Datos SQL**: Accesible local o remotamente (PostgreSQL, SQL Server, MySQL, SQLite, etc.)

### Instalación de dependencias:

```bash
pip install pandas requests sqlalchemy psycopg2 flask pyodbc

```

> *Nota: Adapta o sustituye `psycopg2` o `pyodbc` según los conectores específicos que requiera tu motor de base de datos.*

---

## ▶️ Modos de Uso y Ejecución

### Modo A: Orquestador Interactivo por Consola (ETL Rápida)

1. Define tu clase de entidad personalizada en un archivo (ej: `dataclass_template.py`):
```python
from dataclasses import dataclass

@dataclass
class Persona:
    id: int
    first_name: str
    last_name: str

```


2. Ejecuta el archivo ejecutable asistente: `./SpringlessEasyBatch.exe` (o ejecuta `python batch_processor.py`).
3. Sigue las instrucciones interactivas en pantalla proporcionando: la ruta de tu dataclass, tipo de entrada (`csv`, `api`, `db`), ruta de origen, tipo de destino y tabla destino.

---

### Modo B: Procesamiento Automatizado vía API HTTP (Flask)

#### 1. Preparar el entorno de Datos

Ejecuta el script SQL (`Levantar_Personas.sql`) en tu gestor de base de datos para crear las tablas destino y configura tus credenciales de conexión en `flask_api_personas.py`:

```python
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=mi_base_datos;"
    "UID=usuario;"
    "PWD=contraseña"
)

```

#### 2. Levantar el Servicio Web

* **En Windows**: Haz doble clic sobre el archivo `run_api_personas.bat`.
* **Desde la Consola**:
```bash
python flask_api_personas.py

```



#### 3. Disparar e Iniciar el Proceso Batch

Envía una petición HTTP POST al endpoint expuesto para devorar el archivo `input_personas.csv` e inyectar de forma masiva los registros a la base de datos:

```bash
curl -X POST http://localhost:5000/batch/run

```

---

## 🔧 Ejemplo de Personalización del Pipeline

Puedes extender el comportamiento de `batch_processor.py` de forma manual agregando lógicas personalizadas de manera secuencial antes de escribir los datos en el destino:

```python
def to_uppercase(obj: Persona) -> Persona:
    obj.first_name = obj.first_name.upper()
    return obj

# Instanciación y agregación al Pipeline
procesador = Processor[Persona]()
procesador.add(strip_whitespace) # Limpieza por defecto
procesador.add(to_uppercase)     # Transformación personalizada

```

---

## ⚖️ Licencia y Términos de Uso

Este ecosistema de software cuenta con un modelo de licenciamiento mixto:

* **Fines No Comerciales y Educativos**: Libre distribución, uso personal y de investigación manteniendo el aviso de copyright intacto de manera gratuita. Queda prohibida la ingeniería inversa sobre los módulos compilados (`.exe`) en entornos de producción privada.
* **Código Abierto Relacionado**: Los módulos basados en API se distribuyen bajo los términos de la **Licencia Pública General de GNU versión 3 (GPLv3)**.

Para revisar los detalles legales específicos, consulte el fichero `LICENSE.txt`.

---

## 📬 Contacto

📧 **Email:** bernaldezperedaj@gmail.com

© 2025 JuanitoSoftware












--------------















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
