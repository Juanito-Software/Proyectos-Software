# Configuración de Trovo Chat

Esta guía te ayudará a configurar la integración del chat de Trovo en tu widget de chat unificado.

## 📋 Requisitos Previos

- Cuenta de Trovo activa
- Acceso al [Portal de Desarrolladores de Trovo](https://developer.trovo.live/)

## 🔑 Paso 1: Registrar una Aplicación en Trovo

1. **Accede al Portal de Desarrolladores:**
   - Ve a [https://developer.trovo.live/](https://developer.trovo.live/)
   - Inicia sesión con tu cuenta de Trovo

2. **Crea una Nueva Aplicación:**
   - Navega a la sección **"Aplicaciones"** o **"Applications"**
   - Haz clic en **"Crear Nueva Aplicación"** o **"Create New Application"**
   - Completa el formulario:
     - **Nombre de la aplicación**: Ej: "Unified Chat Widget"
     - **Descripción**: Ej: "Widget de chat unificado para OBS"
     - **URL de redirección** (Redirect URL - campo `developer.label_redirect*`): 
       - ⚠️ **IMPORTANTE**: Este campo es obligatorio (tiene asterisco *)
       - **Formato requerido**: Trovo requiere URLs HTTPS válidas (NO acepta `localhost` ni `http://`)
       - **Solución**: Como no hacemos OAuth interactivo, puedes usar cualquier URL HTTPS válida:
         - `https://example.com` ✅ (recomendado - URL genérica válida)
         - `https://trovo.live` ✅ (URL oficial de Trovo)
         - `https://www.google.com` ✅ (cualquier dominio HTTPS válido)
       - **Puedes añadir múltiples URLs** usando el botón verde con el signo "+" que aparece a la derecha del campo
       - **Nota importante**: Esta URL NO se utiliza realmente para el chat unificado, ya que usamos tokens de servicio directamente (no hacemos OAuth interactivo). Solo es un campo requerido por el formulario de Trovo. Puedes usar cualquier URL HTTPS válida.
       - **Ejemplo**: Escribe `https://example.com` en el campo
   - Haz clic en **"Crear"** o **"Create"**

3. **Obtén tus Credenciales:**
   - Una vez creada la aplicación, verás:
     - **Client ID**: Un identificador único de tu aplicación
     - **Client Secret**: (Ya NO es necesario para el chat - solo se usa para OAuth)
   - **Copia el Client ID** - lo necesitarás para el `.env`

## 🔍 Paso 2: Obtener el Channel ID

El **Channel ID** es el identificador único de tu canal de Trovo. Es el mismo que tu **User ID** como streamer.

### Opción A: Desde la URL de tu Canal (más fácil)
1. Ve a tu canal de Trovo: `https://www.trovo.live/s/[TU_NOMBRE]`
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña "Network" (Red)
4. Recarga la página
5. Busca peticiones a la API de Trovo
6. El Channel ID aparecerá en las respuestas (es un número, ej: `100000021`)

### Opción B: Desde el código fuente
1. Ve a tu canal de Trovo
2. Haz clic derecho → "Ver código fuente" o presiona Ctrl+U
3. Busca (Ctrl+F) por "channel_id" o "user_id"
4. El número que encuentres es tu Channel ID

### Opción C: Usando la API de Trovo
1. Con tu `Client ID`, puedes hacer una petición GET:
   ```bash
   curl -H "Client-ID: TU_CLIENT_ID" \
        -H "Accept: application/json" \
        https://open-api.trovo.live/openplatform/getusers?user=TU_NOMBRE_DE_USUARIO
   ```
2. La respuesta incluirá el `user_id` que es tu `channel_id`

## ⚙️ Paso 3: Configurar el .env

Añade las siguientes variables a tu archivo `.env`:

```env
# TROVO
TROVO_CLIENT_ID=tu_client_id_aqui
TROVO_CHANNEL_ID=tu_channel_id_aqui
```

**Ejemplo:**
```env
# TROVO
TROVO_CLIENT_ID=1234567890abcdef
TROVO_CHANNEL_ID=100000021
```

⚠️ **IMPORTANTE:**
- **Ya NO necesitas** `TROVO_CLIENT_SECRET` - el sistema usa el endpoint `channel-token` que solo requiere Client-ID
- **NUNCA** subas tu archivo `.env` a repositorios públicos
- Mantén estas credenciales seguras

## 🚀 Paso 4: Iniciar el Sistema

Una vez configurado el `.env`, simplemente ejecuta:

```bash
.\run-all-services.bat
```

O si prefieres iniciar solo el chat unificado:

```bash
.\run-unified-chat.bat
```

El sistema intentará conectarse automáticamente a Trovo cuando detecte las credenciales en el `.env`.

## ✅ Verificación

Cuando el sistema esté funcionando, deberías ver en la consola:

```
🔧 [Trovo] Iniciando servicio...
✅ [Trovo] Token obtenido
🔗 [Trovo] WebSocket conectado, autenticando...
✅ [Trovo] Autenticación exitosa
✅ [Trovo] Servicio iniciado
✅ Conectado a Trovo
```

Y cuando lleguen mensajes:

```
💬 [Trovo] Mensaje: Usuario: Hola chat!
```

## 🎨 Personalización

Los usuarios de Trovo aparecerán en el chat con el nombre de usuario en **color naranja fuerte** (`#FF6B35`).

Si quieres cambiar el color, edita `public/chat.html` y modifica:

```css
.username.trovo {
    color:rgb(238, 255, 0); /* Cambia este color */
}
```

## ⚠️ PROBLEMA CONOCIDO: Botón "Create" Deshabilitado

Si el botón "Create" está deshabilitado y no puedes crear la aplicación, esto es un problema conocido del portal de Trovo. Prueba estas soluciones **EN ESTE ORDEN**:

### Solución 1: Verifica tu cuenta de Trovo

1. **Asegúrate de estar logueado correctamente:**
   - Cierra sesión y vuelve a iniciar sesión
   - Verifica que tu cuenta esté activa

2. **Verifica que tu cuenta tenga permisos:**
   - Algunas cuentas nuevas pueden no tener permisos para crear aplicaciones
   - Asegúrate de haber hecho al menos un stream o tener actividad en tu cuenta
   - Algunos usuarios reportan que necesitas tener cierta antigüedad en la cuenta

### Solución 2: Prueba diferentes navegadores

1. **Prueba en modo incógnito:**
   - Chrome: Ctrl+Shift+N
   - Firefox: Ctrl+Shift+P
   - Edge: Ctrl+Shift+N

2. **Prueba otro navegador completamente:**
   - Si estás en Chrome, prueba Firefox o Edge
   - A veces hay problemas de compatibilidad o extensiones que interfieren

3. **Desactiva extensiones del navegador:**
   - Algunas extensiones (adblockers, privacy tools) pueden interferir
   - Prueba desactivarlas temporalmente

### Solución 3: Cambia el idioma y limpia caché

1. **Cambia el idioma del portal a inglés:**
   - Algunos usuarios reportan que funciona mejor en inglés
   - Busca el selector de idioma en la parte superior de la página

2. **Limpia la caché del navegador:**
   - Chrome: Ctrl+Shift+Delete → "Caché" → "Borrar datos"
   - O prueba en modo incógnito

### Solución 4: Inspecciona errores en la consola

1. **Abre la consola del navegador (F12):**
   - Presiona F12 → pestaña "Console"
   - Intenta hacer clic en "Create"
   - Busca errores en rojo que indiquen qué falta
   - Copia cualquier error que aparezca

2. **Revisa la pestaña "Network" (Red):**
   - Intenta hacer clic en "Create"
   - Busca peticiones que fallen (aparecen en rojo)
   - Revisa las respuestas de esas peticiones

### Solución 5: Contacta directamente con soporte de Trovo

Si nada de lo anterior funciona, **contacta directamente con soporte**:

**Email:** customer@trovo.live, developer@trovo.live

**Asunto:** "No puedo crear aplicación - Botón Create deshabilitado"

**Cuerpo del mensaje (copia y pega):**

```
Hola,

Estoy intentando crear una nueva aplicación en el portal de desarrolladores de Trovo, pero el botón "Create" permanece deshabilitado sin razón aparente.

Detalles del problema:
- Todos los campos están completos (nombre, categoría, descripción, redirect URL)
- La URL de redirect es válida (https://example.com)
- El texto "developer.protocolAgreement" aparece dos veces pero no hay checkboxes ni elementos clickeables para aceptar términos
- He probado en diferentes navegadores (Chrome, Firefox, Edge)
- He limpiado la caché y probado en modo incógnito
- No aparecen errores en la consola del navegador

Mi información:
- Nombre de usuario de Trovo: [TU_NOMBRE_AQUI]
- Email de la cuenta: [TU_EMAIL_AQUI]

¿Podrían ayudarme a crear la aplicación o verificar si hay algún problema con mi cuenta?

Adjunto captura de pantalla del formulario.

Gracias.
```

**Incluye:**
- Captura de pantalla del formulario completo
- Captura de la consola del navegador (si hay errores)
- Tu nombre de usuario de Trovo
- Tu email de la cuenta

### Solución 6: Alternativa temporal

Si necesitas el chat de Trovo urgentemente y no puedes crear la aplicación:

1. **Usa temporalmente solo las otras plataformas:**
   - El chat unificado funcionará perfectamente con Twitch, Kick, YouTube y Rumble
   - Puedes añadir Trovo más tarde cuando resuelvas el problema

2. **Pide ayuda a la comunidad:**
   - Busca en foros de Trovo o Discord de desarrolladores
   - Alguien más puede haber tenido el mismo problema y tener una solución

3. **Espera respuesta de soporte:**
   - Trovo suele responder en 1-3 días hábiles
   - Mientras tanto, el sistema funciona perfectamente sin Trovo

## 🔧 Solución de Problemas

### Error: "Faltan credenciales de Trovo en .env"
- **Solución**: Verifica que todas las variables (`TROVO_CLIENT_ID`, `TROVO_CLIENT_SECRET`, `TROVO_CHANNEL_ID`) estén en el `.env` y sin espacios extra

### Error: "Autenticación fallida"
- **Solución**: 
  - Verifica que el `Client ID` y `Client Secret` sean correctos
  - Asegúrate de que el `Channel ID` corresponde a tu canal
  - Verifica que la aplicación esté activa en el portal de desarrolladores

### Error: "Error obteniendo token"
- **Solución**:
  - Verifica tu conexión a internet
  - Comprueba que las credenciales sean válidas
  - Asegúrate de que la API de Trovo esté disponible

### El chat no recibe mensajes
- **Solución**:
  - Verifica que haya un stream activo en tu canal de Trovo
  - Comprueba que el `Channel ID` sea correcto
  - Revisa los logs para ver si hay errores de conexión

### La conexión se cae frecuentemente
- **Solución**: El sistema tiene reconexión automática. Si persiste el problema:
  - Verifica tu conexión a internet
  - Comprueba que el firewall no esté bloqueando la conexión WebSocket
  - Revisa los logs para más detalles

## 📚 Recursos Adicionales

- [Documentación Oficial de Trovo API](https://developer.trovo.live/docs/Chat%20Service.html)
- [Portal de Desarrolladores de Trovo](https://developer.trovo.live/)

## 🔄 Renovación Automática de Token

El sistema renueva automáticamente el token de servicio de chat cada 15 segundos (los tokens son válidos por 20 segundos). Esto asegura que la conexión se mantenga activa sin interrupciones.

## 🎯 Notas Importantes

- El token de servicio de chat de Trovo tiene una validez de **solo 20 segundos**
- El sistema maneja automáticamente la renovación del token
- La conexión WebSocket se mantiene activa mediante ping-pong cada 30 segundos
- Si la conexión se cae, el sistema intentará reconectarse automáticamente

---

**¿Necesitas ayuda?** Revisa los logs del sistema para más detalles sobre cualquier error.

