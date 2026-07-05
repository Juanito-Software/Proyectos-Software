# Configuración de BitChute Chat

Esta guía te ayudará a configurar la integración del chat de BitChute en tu widget de chat unificado.

## 📋 Requisitos Previos

- Cuenta de BitChute activa
- Canal de BitChute con transmisiones en vivo
- Python 3.x instalado (para el servidor intermedio de scraping)

## ⚠️ Limitaciones Importantes

**BitChute NO proporciona una API pública oficial** para acceder a los mensajes del chat en vivo. Por lo tanto, esta integración requiere:

1. **Servidor Python intermedio**: Similar al servidor de Rumble, necesitarás un servidor Python que haga scraping de los mensajes del chat
2. **Video ID**: Necesitarás proporcionar el ID del video en vivo manualmente
3. **Mantenimiento**: El scraping puede requerir actualizaciones si BitChute cambia su estructura

## 🔍 Paso 1: Obtener el Video ID

El **Video ID** es necesario para identificar el stream en vivo de BitChute. Aquí te explico cómo obtenerlo durante tu primer stream:

### Método Recomendado: Desde la URL del Stream en Vivo

1. **Inicia tu transmisión en vivo en BitChute:**
   - Ve a tu canal de BitChute
   - Inicia una transmisión en vivo
   - Copia la URL del video/stream

2. **Copia la URL completa del stream:**
   - La URL aparecerá en la página del stream o en la barra de direcciones del navegador
   - **Formato típico**: `https://www.bitchute.com/video/[VIDEO_ID]/`
   - **Ejemplo**: `https://www.bitchute.com/video/abc123xyz456/`

3. **Extrae el Video ID de la URL:**
   - El **Video ID** es la parte que está después de `/video/` y antes del `/` final
   - **Ejemplo**: 
     - URL: `https://www.bitchute.com/video/abc123xyz456/`
     - Video ID: `abc123xyz456`

4. **Añádelo a tu `.env`:**
   ```env
   BITCHUTE_VIDEO_ID=abc123xyz456
   ```

### Método Alternativo: Si ya tienes el stream abierto

Si ya tienes el stream corriendo y no recuerdas la URL:

1. **Desde la barra de direcciones del navegador:**
   - Abre la página donde estás viendo/transmitiendo el stream
   - Copia la URL completa de la barra de direcciones
   - Extrae el Video ID como se explica arriba

2. **Desde el código fuente de la página:**
   - Abre la página del video en vivo
   - Haz clic derecho → "Ver código fuente" o presiona `Ctrl+U`
   - Busca (Ctrl+F) por `video` o `video_id` o el ID que viste en la URL
   - El Video ID aparecerá en el código

3. **Desde las herramientas de desarrollador:**
   - Abre las herramientas de desarrollador (F12)
   - Ve a la pestaña "Network" (Red)
   - Recarga la página (F5)
   - Busca peticiones que contengan el Video ID en la URL o en los datos

### ⚠️ Nota Importante

- **El Video ID es específico de cada stream**: Cada vez que inicies un nuevo stream en vivo, obtendrás un Video ID diferente
- **Debes actualizar el `.env`** cada vez que inicies un nuevo stream si quieres capturar ese stream específico
- **El Video ID solo funciona mientras el stream esté activo**: Una vez que termines el stream, ese Video ID ya no será válido para capturar mensajes en tiempo real

## ⚙️ Paso 2: Configurar el .env

Añade las siguientes variables a tu archivo `.env`:

```env
# BITCHUTE
BITCHUTE_CHANNEL_NAME=tu_canal_bitchute
BITCHUTE_VIDEO_ID=tu_video_id_aqui
BITCHUTE_SERVER_URL=http://localhost:5005
```

**Ejemplo:**
```env
# BITCHUTE
BITCHUTE_CHANNEL_NAME=juanito
BITCHUTE_VIDEO_ID=abc123xyz
BITCHUTE_SERVER_URL=http://localhost:5005
```

⚠️ **IMPORTANTE:**
- **BITCHUTE_VIDEO_ID es REQUERIDO** - BitChute no tiene API para obtenerlo automáticamente
- **Debes obtenerlo manualmente** desde la URL del stream en vivo (ver Paso 1)
- **El Video ID cambia con cada stream**: Cada vez que inicies un nuevo stream, obtendrás un Video ID diferente
- **Actualiza el `.env`** cada vez que inicies un nuevo stream si quieres capturar ese stream específico
- **BITCHUTE_CHANNEL_NAME** es opcional pero recomendado para referencia
- **BITCHUTE_SERVER_URL** es la URL del servidor Python intermedio (por defecto: `http://localhost:5005`)
- **NUNCA** subas tu archivo `.env` a repositorios públicos
- Mantén estas credenciales seguras

### 💡 Consejo Práctico

Para facilitar el proceso durante tus streams:
1. **Antes de empezar el stream**: Prepara tu `.env` con un Video ID temporal (puedes usar cualquier valor)
2. **Cuando inicies el stream**: Obtén el Video ID real de la URL
3. **Actualiza el `.env`** con el Video ID real
4. **Reinicia el servidor de BitChute** o simplemente espera al siguiente ciclo de polling (5 segundos)

## 🐍 Paso 3: Configurar el Servidor Python Intermedio

BitChute requiere un servidor Python que haga scraping de los mensajes del chat. **¡Buenas noticias!** Ya está incluido: `bitchute_server.py`

### Instalar Dependencias

1. **Instalar las dependencias necesarias:**
   ```bash
   pip install flask flask-cors requests beautifulsoup4 python-dotenv
   ```
   
   O si usas el entorno virtual de Python:
   ```bash
   coqui_env\Scripts\python.exe -m pip install flask flask-cors requests beautifulsoup4 python-dotenv
   ```

### Iniciar el Servidor

El servidor se puede iniciar de dos formas:

#### Opción A: Inicio Automático (Recomendado)

Si tienes `BITCHUTE_VIDEO_ID` configurado en tu `.env`, el servidor se iniciará automáticamente cuando ejecutes:
```bash
python bitchute_server.py
```

#### Opción B: Inicio Manual

Si prefieres iniciarlo manualmente o no tienes el VIDEO_ID en `.env`:
```bash
python bitchute_server.py
```

Luego, inicia el chat usando el endpoint `/start`:
```bash
curl -X POST http://localhost:5005/start -H "Content-Type: application/json" -d '{"video_id": "tu_video_id_aqui"}'
```

### Verificar que el Servidor Está Funcionando

El servidor debería mostrar:
```
🚀 Servidor BitChute iniciando en puerto 5005
✅ Auto-conectado a BitChute: tu_video_id
✅ Hilo de chat iniciado
🔄 Iniciando captura de mensajes del chat...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5005
```

### Nota sobre Scraping

El servidor usa técnicas de scraping para extraer mensajes del HTML de BitChute. Esto significa:
- **Puede ser más lento** que APIs oficiales
- **Puede requerir actualizaciones** si BitChute cambia su estructura
- **Respeta los términos de servicio** - el scraping es solo para lectura, no modifica nada

## 🚀 Paso 4: Iniciar el Sistema

Una vez configurado el `.env` y el servidor Python:

1. **Inicia el servidor Python de BitChute** (si lo tienes):
   ```bash
   python bitchute_server.py
   ```

2. **Inicia el chat unificado:**
   ```bash
   .\run-all-services.bat
   ```

El sistema intentará conectarse automáticamente a BitChute cuando detecte las credenciales en el `.env`.

## 🔄 Método de Conexión

El servicio de BitChute utiliza:

### Polling HTTP
- Hace peticiones periódicas al servidor Python intermedio cada 5 segundos
- El servidor Python hace scraping de los mensajes del chat
- Los mensajes se devuelven en formato JSON

### Sin Servidor Intermedio
- Si el servidor Python no está disponible, el servicio mostrará advertencias
- Los mensajes no se recibirán hasta que el servidor esté configurado

## ✅ Verificación

Cuando el sistema esté funcionando, deberías ver en la consola:

```
🔧 [BitChute] Iniciando servicio...
✅ [BitChute] Servicio iniciado (Polling)
💡 [BitChute] Nota: BitChute requiere un servidor Python intermedio para scraping. Consulta BITCHUTE_SETUP.md
```

Y cuando lleguen mensajes (si el servidor está configurado):
```
💬 [BitChute] Mensaje: Usuario: Hola chat!
```

## 🎨 Personalización

Los usuarios de BitChute aparecerán en el chat con el nombre de usuario en **color azul oscuro** (`#00008B`).

Si quieres cambiar el color, edita `public/chat.html` y modifica:

```css
.username.bitchute {
    color: #00008B; /* Cambia este color */
}
```

## 🔧 Solución de Problemas

### Error: "Faltan credenciales de BitChute en .env"
- **Solución**: Verifica que `BITCHUTE_VIDEO_ID` esté en el `.env` (es requerido)

### Error: "Servidor intermedio no disponible"
- **Solución**: 
  - Asegúrate de que el servidor Python de BitChute esté corriendo
  - Verifica que esté en el puerto correcto (por defecto: 5005)
  - Comprueba que `BITCHUTE_SERVER_URL` sea correcta

### El chat no recibe mensajes
- **Solución**:
  - Verifica que haya un stream activo en BitChute
  - Comprueba que el `BITCHUTE_VIDEO_ID` sea correcto y corresponda a un stream en vivo
  - Asegúrate de que el servidor Python esté funcionando y haciendo scraping correctamente
  - Revisa los logs del servidor Python para ver si hay errores

### Error: "BITCHUTE_VIDEO_ID es requerido"
- **Solución**: 
  - BitChute no tiene API para obtener el Video ID automáticamente
  - Debes proporcionarlo manualmente desde la URL del video en vivo
  - Consulta el Paso 1 para obtener el Video ID

## 📚 Recursos Adicionales

- [BitChute Support](https://support.bitchute.com/)
- [BitChute Webhook Integration](https://support.bitchute.com/chatbomb-webhook-integration) (para webhooks, no para leer chat)

## 🎯 Notas Importantes

- **Sin API Pública**: BitChute no proporciona una API pública para el chat, por lo que se requiere scraping
- **Servidor Intermedio Requerido**: Necesitarás un servidor Python que haga scraping de los mensajes
- **Video ID Manual**: Debes proporcionar el Video ID manualmente desde la URL del stream
- **Mantenimiento**: El scraping puede requerir actualizaciones si BitChute cambia su estructura
- **Términos de Servicio**: Asegúrate de cumplir con los términos de servicio de BitChute al hacer scraping

## ⚠️ Consideraciones Legales

- **Términos de Servicio**: Revisa y cumple con los términos de servicio de BitChute
- **Scraping**: El scraping puede estar sujeto a restricciones. Úsalo responsablemente
- **Rate Limiting**: Implementa límites de velocidad para no sobrecargar los servidores de BitChute
- **Privacidad**: Respeta la privacidad de los usuarios y no almacenes datos innecesarios

## 🔄 Desarrollo Futuro

Si decides implementar el servidor Python de scraping:

1. **Analiza la estructura de BitChute**: Usa las herramientas de desarrollador del navegador para entender cómo se cargan los mensajes
2. **Implementa el scraping**: Usa BeautifulSoup o Selenium para extraer los mensajes
3. **Crea la API**: Expone los mensajes a través de una API REST (similar a `rumble_server.py`)
4. **Maneja errores**: Implementa manejo robusto de errores y reconexión

---

**¿Necesitas ayuda?** Revisa los logs del sistema para más detalles sobre cualquier error. La implementación completa del servidor de scraping está fuera del alcance de esta guía básica.

