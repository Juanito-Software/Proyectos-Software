# ✅ ToDoList - Gestor de Tareas de Escritorio

Aplicación de escritorio minimalista y eficiente para **gestionar tus tareas y pendientes diarios**. Con una interfaz gráfica en **Tkinter** y persistencia automática en formato JSON, tus tareas se guardan automáticamente y estarán disponibles cada vez que abras la aplicación.

---

## 🚀 Características

- **Interfaz limpia y minimalista**: Añade, completa y elimina tareas con facilidad desde una ventana de escritorio.
- **Persistencia automática**: Todas las tareas se guardan automáticamente en `tasks.json` al cerrar la aplicación y se restauran al volver a abrirla.
- **Sin dependencias externas**: Usa únicamente la librería estándar de Python (`tkinter`, `json`), sin necesidad de instalar nada.
- **Disponible como ejecutable**: `ToDoList.exe` compilado para Windows, listo para usar sin Python.
- **Marcado de completadas**: Marca tareas como completadas con un checkbox sin eliminarlas, para llevar un registro.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- No requiere instalar ninguna dependencia adicional — usa únicamente librerías estándar de Python.

---

## 📦 Instalación

No es necesaria ninguna instalación. Simplemente descarga o clona el repositorio.

---

## 💻 Uso y Ejecución

### Desde código fuente
```bash
cd ToDoList
python ToDoList.py
```

### Versión ejecutable (sin Python)
Haz doble clic en `ToDoList.exe`.

---

## 📋 Funcionalidad

| Acción | Cómo hacerlo |
|---|---|
| ➕ Añadir tarea | Escribe en el campo de texto y pulsa Enter o el botón "Añadir" |
| ✅ Marcar como completada | Haz clic en el checkbox al lado de la tarea |
| 🗑️ Eliminar tarea | Selecciona la tarea y pulsa el botón "Eliminar" |
| 💾 Guardar | Automático al cerrar la ventana |

---

## 💾 Formato de datos (tasks.json)

Las tareas se almacenan en un archivo JSON simple:

```json
[
  {
    "texto": "Revisar el correo",
    "completada": false
  },
  {
    "texto": "Terminar el proyecto",
    "completada": true
  }
]
```

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta `Licencia/LICENSE.txt` para más detalles.
