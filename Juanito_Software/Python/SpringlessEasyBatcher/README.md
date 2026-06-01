# ⚡ SpringlessEasyBatcher - Batching Masivo de Datos sin Spring

Herramienta ágil en Python para realizar **inserciones masivas (batch)** de datos en bases de datos SQL a través de una **API REST construida con Flask**. Diseñada como alternativa ligera a los procesos batch de Spring Batch, sin necesitar Java ni infraestructura pesada.

---

## 🚀 Características

- **API REST con Flask**: Endpoints HTTP para disparar y controlar el proceso de ingesta de datos.
- **Ingesta desde CSV**: Lee datos del archivo `input_personas.csv` y los inserta masivamente en la base de datos.
- **Dataclasses tipadas**: Usa `dataclass_template.py` para definir el modelo de datos de forma limpia y tipada (Python `dataclasses`).
- **Base de datos de ejemplo**: Incluye script SQL (`Levantar_Personas.sql`) para crear la tabla de prueba con datos de ejemplo.
- **Lanzamiento fácil**: Script `.bat` para levantar la API con un solo doble clic en Windows.
- **Documentación incluida**: `Instrucciones_de_uso.txt` con guía paso a paso del flujo completo.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- **Base de datos SQL** accesible (SQL Server, PostgreSQL, MySQL, SQLite...)
- Dependencias:
  ```bash
  pip install flask pyodbc
  ```
  > Sustituye `pyodbc` por el driver de tu base de datos si es diferente (ej: `psycopg2` para PostgreSQL, `mysql-connector-python` para MySQL).

---

## 📦 Instalación

```bash
cd SpringlessEasyBatcher
pip install flask pyodbc
```

Configura la cadena de conexión a la base de datos en `flask_api_personas.py` según tu entorno:
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

## 💻 Uso y Ejecución

### Paso 1: Preparar la base de datos
Ejecuta el script SQL para crear la tabla de destino:
```sql
-- Ejecutar en tu gestor de base de datos:
-- Crear_BD_Ejemplo/Levantar_Personas.sql
```

### Paso 2: Configurar los datos de entrada
Edita el archivo `input_personas.csv` con los datos a insertar.

### Paso 3: Levantar la API Flask

**Opción A - Windows (automático):**
Doble clic en `run_api_personas.bat`.

**Opción B - Consola:**
```bash
cd SpringlessEasyBatcher
python flask_api_personas.py
```

### Paso 4: Disparar el batch vía HTTP
```bash
# Endpoint para iniciar la carga masiva:
curl -X POST http://localhost:5000/batch/run
```

---

## 📋 Instrucciones completas

Consulta el archivo `Instrucciones_de_uso.txt` para una guía detallada del flujo completo, incluyendo ejemplos de peticiones a la API y configuración avanzada.

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
