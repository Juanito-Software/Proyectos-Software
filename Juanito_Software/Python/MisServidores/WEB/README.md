# Servidor Web en Python

Servidor HTTP/1.1 básico implementado en Python utilizando únicamente la biblioteca estándar (`socket`, `threading`, `os`). Sin dependencias externas.

Este proyecto implementa un servidor web funcional para entornos locales, capaz de parsear peticiones HTTP, servir archivos estáticos y devolver respuestas con el tipo MIME correcto.

---

## ¿Qué hace este programa?

El servidor escucha en `127.0.0.1:8080` y gestiona:

| Método | Ruta | Comportamiento |
|--------|------|----------------|
| `GET` | `/` | Página de inicio HTML o `index.html` de `public/` si existe |
| `GET` | `/hola` | Página "¡Hola desde Python!" |
| `GET` | `/<ruta>` | Archivo de la carpeta `public/` si existe |
| `HEAD` | cualquiera | Igual que GET pero sin body |
| Cualquier otro | — | `405 Method Not Allowed` |

Tipos MIME soportados: `.html`, `.css`, `.js`, `.json`, `.png`, `.jpg`, `.gif`, `.ico`, `.svg`, `.txt`

Cada conexión se atiende en un hilo independiente con `threading`.

---

## Estructura del proyecto

```
├── servidor_web.py       # Todo el servidor en un único módulo
├── ejecutar_servidor.bat # Lanzador con doble clic (Windows)
└── public/               # Carpeta opcional para archivos estáticos
    └── index.html        # Página de inicio (si existe)
```

---

## 1. Ejecución

**Desde terminal** (Python 3.10 o superior):

desde cmd:

```bash
cd <ruta-del-proyecto>
python servidor_web.py
```

desde powershell:

```powershell
cd <ruta-del-proyecto>
python servidor_web.py
```

**Desde Windows con doble clic:**

Ejecuta `ejecutar_servidor.bat`. Abre una consola, arranca el servidor y mantiene la ventana abierta. Para detenerlo, `Ctrl+C` o cierra la ventana.

---

## 2. Prueba en el navegador

Con el servidor en marcha, abre:

- `http://127.0.0.1:8080` → página de inicio
- `http://127.0.0.1:8080/hola` → página "¡Hola desde Python!"
- `http://127.0.0.1:8080/<ruta>` → archivo de `public/` si existe

---

## Estado del proyecto

- Servidor HTTP funcional en entorno local
- Sin dependencias externas
- Probado con navegador estándar
- Implementación educativa (no production-ready)

---

## Objetivo del proyecto

Proyecto de aprendizaje sobre:

- Protocolo HTTP/1.1 a bajo nivel
- Sockets TCP en Python
- Parseo manual de peticiones HTTP
- Tipos MIME y servicio de archivos estáticos
- Concurrencia básica con hilos (`threading`)
- Implementación de protocolo desde cero sin dependencias externas
