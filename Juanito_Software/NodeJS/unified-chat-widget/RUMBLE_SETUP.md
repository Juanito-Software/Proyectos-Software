# Configuración de Rumble para Chat Unificado

## 📋 Requisitos Previos

1. **Instalar dependencias de Python:**
   ```bash
   coqui_env\Scripts\python.exe -m pip install flask flask-cors cocorum python-dotenv
   ```
   
   ⚠️ **Nota:** Si ya instalaste las dependencias anteriormente, puedes saltarte este paso.

2. **Obtener la URL de la API de Rumble:**
   - ⚠️ **IMPORTANTE:** `cocorum` necesita una "API URL with key" específica, NO la URL pública del canal
   - Esta URL se obtiene desde tu panel de Rumble como streamer
   - La URL tiene el formato: `https://rumble.com/-livestream-api/get-data?key=[TU-CLAVE]`
   - **Cómo encontrarla:**
     - Accede a tu panel de streamer en Rumble
     - Busca la sección de "API" o "Live Stream API"
     - Copia la URL completa que incluye tu clave de API (incluye el parámetro `?key=...`)
   - Ejemplo: `https://rumble.com/-livestream-api/get-data?key=TCIqDt7EFyXancF_AB2rIvgmXLRbTW_2ijLGAps3ayZ7BwYxU2JVAcn1fPSnoD7DJ-FnrmgsV8FBLwX4-2u9SA`

## 🔧 Configuración en .env

Añade estas variables a tu archivo `.env`:

```env
# RUMBLE
RUMBLE_API_URL=https://rumble.com/-livestream-api/get-data?key=TU-CLAVE-AQUI
RUMBLE_CHANNEL=JuanitoCanuto
RUMBLE_SERVER_URL=http://localhost:5003
RUMBLE_POLL_INTERVAL=3000
RUMBLE_REFRESH_RATE=5
RUMBLE_SERVER_PORT=5003
```

### Variables explicadas:

- **RUMBLE_API_URL**: URL completa de la API de Rumble con tu clave (ej: `https://rumble.com/-livestream-api/get-data?key=TCIqDt7EFyXancF_AB2rIvgmXLRbTW_2ijLGAps3ayZ7BwYxU2JVAcn1fPSnoD7DJ-FnrmgsV8FBLwX4-2u9SA`)
   - ⚠️ **IMPORTANTE:** Esta es la URL de la API con tu clave, NO la URL pública del canal
- **RUMBLE_CHANNEL**: Nombre de tu canal (opcional, para referencia)
- **RUMBLE_SERVER_URL**: URL del servidor Python de Rumble (por defecto: `http://localhost:5003`)
- **RUMBLE_POLL_INTERVAL**: Intervalo en milisegundos para obtener mensajes (por defecto: 3000ms = 3 segundos)
- **RUMBLE_REFRESH_RATE**: Tasa de actualización en segundos para cocorum (por defecto: 5 segundos)
- **RUMBLE_SERVER_PORT**: Puerto donde corre el servidor Python (por defecto: 5003)

## 🚀 Uso

### Inicio del Chat Unificado

El servidor de Rumble se inicia **automáticamente** cuando ejecutas el chat unificado:

```bash
run-unified-chat.bat
```

Esto iniciará:
1. El servidor de Rumble en segundo plano (Python)
2. El servidor de chat unificado (Node.js)

**Ventaja:** Solo necesitas ejecutar un archivo y todo funciona automáticamente.

### Actualizar configuración automáticamente (antes de cada directo)

Si necesitas cambiar la URL de Rumble antes de cada directo, puedes usar el script de automatización:

#### Opción A: Actualización manual
```bash
update-rumble-env.bat --api-url "https://rumble.com/c/tu-canal" --channel "tu-canal"
```

**Ejemplo:**
```bash
update-rumble-env.bat --api-url "https://rumble.com/c/JuanitoCanuto" --channel "JuanitoCanuto"
```

#### Opción B: Detección automática
```bash
update-rumble-env.bat --auto-detect
```

Esto intentará detectar automáticamente tu stream activo y actualizar el `.env`.

## 🔄 Flujo de Trabajo Recomendado

### Primera vez (Configuración inicial):

1. **Configurar `.env`:**
   - Añade las variables de Rumble a tu archivo `.env` (ver sección de configuración arriba)
   - Asegúrate de tener la URL correcta de tu canal

2. **Instalar dependencias (si no lo has hecho):**
   ```bash
   coqui_env\Scripts\python.exe -m pip install flask flask-cors cocorum python-dotenv
   ```

### Antes de cada directo:

1. **Actualizar URL (si es necesario):**
   - Si cambias de canal o URL, ejecuta:
     ```bash
     update-rumble-env.bat --api-url "https://rumble.com/c/tu-canal-nuevo" --channel "tu-canal-nuevo"
     ```
   - O usa detección automática:
     ```bash
     update-rumble-env.bat --auto-detect
     ```

2. **Iniciar servicios:**
   - Ejecuta `run-TTS.bat` (servidor TTS, opcional)
   - Ejecuta `run-unified-chat.bat` (esto iniciará automáticamente Rumble + chat unificado)

3. **Verificar conexión:**
   - Revisa los logs en la consola
   - Deberías ver:
     ```
     [INFO] Iniciando servidor de Rumble en segundo plano...
     ✅ [Rumble] Conectado: https://rumble.com/c/tu-canal
     ✅ Conectado a Rumble
     ```

### Durante el directo:

- Los mensajes de Rumble aparecerán en el chat unificado con el nombre de usuario en **azul eléctrico** (#00BFFF)
- Los mensajes se procesan igual que los de Twitch, Kick y YouTube (comandos, TTS, etc.)

## ⚠️ Notas Importantes

- **Inicio automático:** Si usas `run-unified-chat.bat`, el servidor de Rumble se inicia automáticamente en segundo plano
- **Stream en vivo:** Si no hay stream en vivo en Rumble, el sistema seguirá intentando conectarse pero no recibirá mensajes hasta que inicies el stream
- **Polling:** El sistema usa polling (consultas periódicas cada 3 segundos) para obtener mensajes, no WebSockets en tiempo real
- **Cambio de URL:** Si cambias la URL de Rumble en el `.env`, reinicia el chat unificado para que tome los cambios
- **Color en el chat:** Los nombres de usuario de Rumble aparecen en **azul eléctrico** (#00BFFF) en el widget de chat

## 🐛 Solución de Problemas

### Error: "No se pudo conectar" o "ECONNREFUSED"
- **Causa:** El servidor de Rumble no está corriendo o el puerto 5003 está ocupado
- **Solución:**
  - El servidor de Rumble debería iniciarse automáticamente con `run-unified-chat.bat`. Verifica los logs
  - Verifica que `RUMBLE_SERVER_URL` en `.env` sea `http://localhost:5003`
  - Cierra cualquier otra aplicación que use el puerto 5003
  - Reinicia `run-unified-chat.bat` si el servidor no se inició correctamente

### Error: "Falta RUMBLE_API_URL"
- **Causa:** No has configurado la URL de Rumble en el `.env`
- **Solución:**
  - Añade `RUMBLE_API_URL=https://rumble.com/c/tu-canal` a tu archivo `.env`
  - Reemplaza `tu-canal` con el nombre real de tu canal
  - Reinicia el chat unificado después de cambiar el `.env`

### No se reciben mensajes de Rumble
- **Causa 1:** No hay stream en vivo
  - **Solución:** Asegúrate de tener un stream activo en Rumble
- **Causa 2:** URL incorrecta
  - **Solución:** Verifica que `RUMBLE_API_URL` apunte a tu canal correcto
- **Causa 3:** El servidor de Rumble no está conectado
  - **Solución:** Revisa los logs del servidor de Rumble para ver errores
  - Busca mensajes como: `✅ [Rumble] Conectado: [TU_URL]`

### Error: "ModuleNotFoundError: No module named 'cocorum'"
- **Causa:** No has instalado las dependencias de Python
- **Solución:**
  ```bash
  coqui_env\Scripts\python.exe -m pip install flask flask-cors cocorum python-dotenv
  ```

### Los mensajes de Rumble no aparecen en el chat
- **Causa:** El servidor de Rumble no está enviando mensajes o hay un error en la conexión
- **Solución:**
  1. Verifica que el servidor de Rumble esté corriendo (deberías ver logs en la consola)
  2. Verifica que haya un stream en vivo
  3. Revisa la consola del navegador (F12) para ver errores de WebSocket
  4. Verifica que el chat unificado muestre: `✅ Conectado a Rumble`

## 📚 Referencias

- [cocorum en PyPI](https://pypi.org/project/cocorum/)
- [Documentación de cocorum](https://pypi.org/project/cocorum/)

