# 🖥️ MisServidores - Servidores Locales de Utilidad

Colección de **servidores locales ligeros** para uso doméstico o en red local (LAN), implementados en Python puro. Actualmente incluye un **servidor FTP** para transferencia de archivos y un **servidor web HTTP** para compartir contenido estático.

---

## 📂 Estructura del Proyecto

```
MisServidores/
├── FTP/
│   ├── servidor_ftp.py      # Servidor FTP completo con pyftpdlib
│   └── README.md            # Instrucciones específicas del servidor FTP
└── WEB/
    ├── servidor_web.py      # Servidor HTTP básico con http.server
    ├── ejecutar_servidor.bat # Lanzador rápido para Windows
    └── README.md            # Instrucciones específicas del servidor web
```

---

## 🚀 Características

### 📡 Servidor FTP (`FTP/servidor_ftp.py`)
- Servidor FTP completo basado en **pyftpdlib**, una de las librerías FTP más rápidas en Python.
- Permite conexiones de múltiples clientes simultáneos.
- Configurable: directorio raíz, usuarios, permisos y puerto.
- Compatible con cualquier cliente FTP estándar (FileZilla, Total Commander, etc.).

### 🌐 Servidor Web HTTP (`WEB/servidor_web.py`)
- Servidor HTTP estático basado en el módulo estándar `http.server` de Python.
- Ideal para compartir archivos en red local o testear páginas HTML estáticas.
- Lanzamiento instantáneo sin configuración previa.

---

## 🛠️ Requisitos del Sistema

- **Python 3.9+**
- Solo para el servidor FTP:
  ```bash
  pip install pyftpdlib
  ```
- El servidor web usa únicamente librerías estándar (sin instalación adicional).

---

## 📦 Instalación

```bash
# Solo necesario para el servidor FTP
pip install pyftpdlib
```

---

## 💻 Uso y Ejecución

### Servidor FTP
```bash
cd FTP
python servidor_ftp.py
```
El servidor arrancará por defecto en el puerto **21** (o el configurado en el script). Conéctate desde cualquier cliente FTP usando la IP local de tu máquina.

### Servidor Web HTTP

**Opción A - Lanzador automático (Windows):**
Haz doble clic en `WEB/ejecutar_servidor.bat`.

**Opción B - Desde la consola:**
```bash
cd WEB
python servidor_web.py
```
El servidor estará disponible en `http://localhost:8080` (o el puerto configurado).

---

## ⚖️ Licencia

Este proyecto está licenciado bajo la **Licencia Pública General de GNU versión 3 (GPLv3)**. Consulta el archivo `README.md` dentro de cada subcarpeta para más detalles.
