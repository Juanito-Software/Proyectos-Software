# Configuración de DLive Chat

Esta guía te ayudará a configurar la integración del chat de DLive en tu widget de chat unificado.

## 📋 Requisitos Previos

- Cuenta de DLive activa
- Canal de DLive con transmisiones en vivo
- Acceso a la [API de DLive](https://docs.dlive.tv/)

## 🔑 Paso 1: Obtener un Token de Acceso

⚠️ **PROBLEMA CONOCIDO**: DLive no proporciona una forma clara y oficial de obtener tokens de acceso. El proceso puede ser frustrante. Hemos creado un script helper para facilitarlo.

### Método 1: Script Helper Automático (RECOMENDADO)

1. **Abre tu canal de DLive en el navegador:**
   - Ve a `https://dlive.tv/[TU_USUARIO]` (reemplaza `[TU_USUARIO]` con tu nombre de usuario)
   - **Asegúrate de estar logueado** en tu cuenta de DLive
   - Abre las herramientas de desarrollador (presiona F12)
   - Ve a la pestaña **"Console"** (Consola)

2. **Ejecuta el script helper:**
   - Abre el archivo `utils/get-dlive-token.js` en tu editor
   - Copia TODO el contenido del archivo
   - Pégalo en la consola del navegador y presiona Enter
   - El script buscará automáticamente el token en varios lugares

3. **Copia el token encontrado:**
   - El script mostrará el token si lo encuentra
   - Copia el valor y añádelo a tu `.env`

### Método 2: Búsqueda Manual en Network (Si el script no funciona)

1. **Abre tu canal de DLive en el navegador:**
   - Ve a `https://dlive.tv/[TU_USUARIO]`
   - **Asegúrate de estar logueado**
   - Abre las herramientas de desarrollador (F12)

2. **Busca el token en las peticiones:**
   - Ve a la pestaña **"Network"** (Red)
   - Recarga la página (F5) para capturar las peticiones
   - Busca peticiones a `api.dlive.tv` o `api-ws.dlive.tv`
   - Haz clic en una de las peticiones
   - Ve a la pestaña **"Headers"** (Encabezados)
   - En **"Request Headers"**, busca **"Authorization"** o **"authorization"**
   - El token puede aparecer como:
     - `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (copia solo la parte después de "Bearer ")
     - O directamente: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Copia el token completo**

3. **Si no aparece en Network:**
   - Ve a la pestaña **"Application"** (Aplicación)
   - Busca en **"Local Storage"** → `https://dlive.tv`
   - Busca claves como `token`, `auth`, `access`, `authorization`
   - También revisa **"Session Storage"**

### Método 3: Intentar sin Token (Experimental)

El servicio ahora puede intentar conectarse sin token. Esto puede funcionar para leer mensajes públicos, pero puede fallar si DLive requiere autenticación:

1. **Solo configura el username en `.env`:**
   ```env
   DLIVE_STREAMER_USERNAME=tu_usuario
   # DLIVE_ACCESS_TOKEN= (deja esto vacío o comenta la línea)
   ```

2. **El sistema intentará conectarse sin token**
   - Si funciona, ¡genial! No necesitas token
   - Si falla, necesitarás obtener el token usando los métodos anteriores

⚠️ **IMPORTANTE:** 
- El token es de tu sesión personal y puede expirar
- Si el token expira, necesitarás obtener uno nuevo
- Mantén el token seguro y no lo compartas públicamente
- **DLive no facilita obtener tokens**, lo cual es frustrante pero es la realidad actual

### Método 4: OAuth2 (Avanzado - Puede no estar disponible)

1. **Consulta la documentación oficial:**
   - Ve a [https://docs.dlive.tv/](https://docs.dlive.tv/)
   - Busca la sección de [Autenticación OAuth2](https://docs.dlive.tv/api/authentication-oauth2/scopes)
   - **Nota**: Puede que esta documentación no esté completa o actualizada

2. **Contacta a soporte de DLive:**
   - Si necesitas un token para una aplicación, contacta directamente a DLive
   - Ellos pueden proporcionar instrucciones específicas

## 🔍 Paso 2: Obtener el Nombre de Usuario del Streamer

El **Streamer Username** es simplemente el nombre de usuario de tu canal en DLive.

**Ejemplos:**
- Si tu canal es `https://dlive.tv/juanito`, el username es: `juanito`
- Si tu canal es `https://dlive.tv/mi_canal`, el username es: `mi_canal`

**Nota:** No incluyas el símbolo `@` ni espacios. Solo el nombre de usuario.

## ⚙️ Paso 3: Configurar el .env

Añade las siguientes variables a tu archivo `.env`:

```env
# DLIVE
DLIVE_STREAMER_USERNAME=tu_nombre_de_usuario_aqui
DLIVE_ACCESS_TOKEN=tu_token_de_acceso_aqui
```

**Ejemplo con token:**
```env
# DLIVE
DLIVE_STREAMER_USERNAME=juanito
DLIVE_ACCESS_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Ejemplo sin token (experimental):**
```env
# DLIVE
DLIVE_STREAMER_USERNAME=juanito
# DLIVE_ACCESS_TOKEN= (deja vacío para intentar sin token)
```

⚠️ **IMPORTANTE:**
- **NUNCA** subas tu archivo `.env` a repositorios públicos
- Mantén estas credenciales seguras
- El token puede expirar - verifica la validez periódicamente
- Si el token expira, necesitarás obtener uno nuevo
- **El token es OPCIONAL** - el sistema intentará funcionar sin él, pero puede fallar si DLive requiere autenticación

## 🚀 Paso 4: Iniciar el Sistema

Una vez configurado el `.env`, simplemente ejecuta:

```bash
.\run-all-services.bat
```

O si prefieres iniciar solo el chat unificado:

```bash
.\run-unified-chat.bat
```

El sistema intentará conectarse automáticamente a DLive cuando detecte las credenciales en el `.env`.

## 🔄 Método de Conexión

El servicio de DLive utiliza:

### WebSocket con GraphQL Subscriptions
- Se conecta al WebSocket de DLive: `wss://api-ws.dlive.tv`
- Autentica con el token de acceso
- Se suscribe a eventos de chat usando GraphQL
- Recibe mensajes en tiempo real mediante la suscripción `streamMessageReceived`

### Keep-Alive
- El servidor envía mensajes "ka" (keep-alive) cada 25 segundos
- El sistema verifica que estos mensajes lleguen
- Si no se reciben en 30 segundos, se reconecta automáticamente

## ✅ Verificación

Cuando el sistema esté funcionando, deberías ver en la consola:

```
🔧 [DLive] Iniciando servicio...
🔗 [DLive] WebSocket conectado, autenticando...
✅ [DLive] Autenticación exitosa, suscribiéndose al chat...
📡 [DLive] Suscrito al chat de juanito
✅ [DLive] Suscripción completada
✅ [DLive] Servicio iniciado
✅ Conectado a DLive
```

Y cuando lleguen mensajes:
```
💬 [DLive] Mensaje: Usuario: Hola chat!
```

## 🎨 Personalización

Los usuarios de DLive aparecerán en el chat con el nombre de usuario en **color dorado** (`#FFD700`).

Si quieres cambiar el color, edita `public/chat.html` y modifica:

```css
.username.dlive {
    color: #FFD700; /* Cambia este color */
}
```

## 🔧 Solución de Problemas

### Error: "Faltan credenciales de DLive en .env"
- **Solución**: Verifica que ambas variables (`DLIVE_ACCESS_TOKEN` y `DLIVE_STREAMER_USERNAME`) estén en el `.env` y sin espacios extra

### Error: "Autenticación fallida"
- **Solución**: 
  - Verifica que el `DLIVE_ACCESS_TOKEN` sea válido y no haya expirado
  - Asegúrate de que el token tenga los permisos necesarios para leer el chat
  - Intenta obtener un nuevo token

### Error: "Error conectando"
- **Solución**:
  - Verifica tu conexión a internet
  - Comprueba que la API de DLive esté disponible
  - Revisa que el WebSocket no esté bloqueado por firewall

### Error: "No se recibió keep-alive, reconectando..."
- **Solución**: 
  - Esto puede indicar problemas de red intermitentes
  - El sistema se reconectará automáticamente
  - Verifica la estabilidad de tu conexión a internet
  - Si persiste, puede ser que el token haya expirado

### El chat no recibe mensajes
- **Solución**:
  - Verifica que haya un stream activo en tu canal de DLive
  - Comprueba que el `DLIVE_STREAMER_USERNAME` sea correcto (sin @, sin espacios)
  - Asegúrate de que el token tenga permisos para leer el chat
  - Revisa los logs para ver si hay errores de suscripción

### La conexión se cae frecuentemente
- **Solución**: 
  - El sistema tiene reconexión automática
  - Verifica tu conexión a internet
  - Comprueba que el firewall no esté bloqueando la conexión WebSocket
  - Verifica que el token no haya expirado
  - Revisa los logs para más detalles

### Error: "Suscripción fallida"
- **Solución**:
  - Verifica que el `DLIVE_STREAMER_USERNAME` sea correcto
  - Asegúrate de que el streamer tenga un stream activo
  - Comprueba que el token tenga permisos para suscribirse a eventos

## 📚 Recursos Adicionales

- [Documentación Oficial de DLive API](https://docs.dlive.tv/)
- [API Subscription WebSocket](https://docs.dlive.tv/api/api/subscription-web-socket)
- [Autenticación OAuth2 de DLive](https://docs.dlive.tv/api/authentication-oauth2/scopes)

## 🔄 Reconexión Automática

El sistema tiene reconexión automática:
- Si el WebSocket se desconecta, intentará reconectarse después de 5 segundos
- Si no se reciben mensajes keep-alive, se reconectará automáticamente
- Los mensajes se seguirán recibiendo mientras haya conexión

## 🎯 Notas Importantes

- **Token de Acceso**: El token puede tener una validez limitada. Si expira, necesitarás obtener uno nuevo.
- **GraphQL**: DLive usa GraphQL para las suscripciones, lo que permite consultas flexibles.
- **Keep-Alive**: El servidor envía mensajes "ka" cada 25 segundos. El sistema verifica estos mensajes para mantener la conexión activa.
- **Suscripciones**: El sistema se suscribe automáticamente a `streamMessageReceived` para recibir mensajes de chat en tiempo real.

## ⚠️ Limitaciones Conocidas

1. **Token de Acceso**: Los tokens pueden expirar. Necesitarás renovarlos periódicamente según la política de DLive.

2. **Requisito de Stream Activo**: El chat solo está disponible cuando hay una transmisión en vivo activa.

3. **Permisos del Token**: Asegúrate de que el token tenga los permisos necesarios para leer el chat del streamer.

4. **Cambios en la API**: Si DLive actualiza su API, puede ser necesario actualizar el servicio.

## 🔐 Seguridad

- **NUNCA** compartas tu token de acceso públicamente
- **NUNCA** subas tu archivo `.env` a repositorios públicos
- Si tu token se compromete, revócalo inmediatamente y genera uno nuevo
- Usa tokens con los permisos mínimos necesarios

---

**¿Necesitas ayuda?** Revisa los logs del sistema para más detalles sobre cualquier error. Si encuentras problemas específicos con la API de DLive, consulta la documentación oficial o contacta al soporte de DLive.

