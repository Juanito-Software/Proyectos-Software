# Configuración de Odysee Chat

Esta guía te ayudará a configurar la integración del chat de Odysee en tu widget de chat unificado.

## 📋 Requisitos Previos

- Cuenta de Odysee activa
- Canal de Odysee con transmisiones en vivo

## 🔍 Paso 1: Obtener el Claim ID o Channel Name

Odysee requiere el **Claim ID** de tu canal para conectarse al chat. Tienes dos opciones:

### Opción A: Usar el Channel Name (más fácil)

Si conoces el nombre de tu canal de Odysee (por ejemplo, `@tu_canal` o `tu_canal`), puedes usar directamente el nombre del canal. El sistema intentará obtener el Claim ID automáticamente.

**Ejemplo:**
- Si tu canal es `@juanito`, usa: `juanito` (sin el @)
- Si tu canal es `@mi_canal_odysee`, usa: `mi_canal_odysee`

### Opción B: Obtener el Claim ID directamente

El **Claim ID** es un identificador único de tu canal en la blockchain de LBRY/Odysee.

#### Método 1: Desde la URL de tu Canal
1. Ve a tu canal de Odysee: `https://odysee.com/@TU_CANAL`
2. Abre las herramientas de desarrollador (F12)
3. Ve a la pestaña "Network" (Red)
4. Recarga la página
5. Busca peticiones a la API de Odysee
6. El Claim ID aparecerá en las respuestas (es una cadena alfanumérica larga)

#### Método 2: Desde el código fuente
1. Ve a tu canal de Odysee
2. Haz clic derecho → "Ver código fuente" o presiona Ctrl+U
3. Busca (Ctrl+F) por `claim_id` o `claimId`
4. El valor que encuentres es tu Claim ID

#### Método 3: Usando la API de Odysee
1. Puedes hacer una petición GET:
   ```bash
   curl "https://api.odysee.live/claim/resolve?name=@TU_CANAL"
   ```
2. La respuesta incluirá el `claim_id` en el campo correspondiente

## ⚙️ Paso 2: Configurar el .env

Añade las siguientes variables a tu archivo `.env`:

### Opción A: Usando Channel Name (recomendado)
```env
# ODYSEE
ODYSEE_CHANNEL_NAME=tu_canal_aqui
```

**Ejemplo:**
```env
# ODYSEE
ODYSEE_CHANNEL_NAME=juanito
```

### Opción B: Usando Claim ID directamente
```env
# ODYSEE
ODYSEE_CLAIM_ID=tu_claim_id_aqui
```

**Ejemplo:**
```env
# ODYSEE
ODYSEE_CLAIM_ID=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

⚠️ **IMPORTANTE:**
- Solo necesitas **UNA** de las dos opciones (Channel Name o Claim ID)
- Si proporcionas ambos, el sistema usará el Claim ID directamente
- **NUNCA** subas tu archivo `.env` a repositorios públicos
- Mantén estas credenciales seguras

## 🚀 Paso 3: Iniciar el Sistema

Una vez configurado el `.env`, simplemente ejecuta:

```bash
.\run-all-services.bat
```

O si prefieres iniciar solo el chat unificado:

```bash
.\run-unified-chat.bat
```

El sistema intentará conectarse automáticamente a Odysee cuando detecte las credenciales en el `.env`.

## 🔄 Métodos de Conexión

El servicio de Odysee intenta dos métodos de conexión:

### Método 1: WebSocket (preferido)
- Se conecta directamente al WebSocket de Odysee: `wss://sockety.odysee.com/ws/commentron`
- Proporciona mensajes en tiempo real
- Se usa automáticamente si la conexión es exitosa

### Método 2: Polling (respaldo)
- Si el WebSocket falla, el sistema cambia automáticamente a polling
- Hace peticiones periódicas a la API de Odysee cada 3 segundos
- Menos eficiente pero más confiable si hay problemas de red

El sistema elegirá automáticamente el mejor método disponible.

## ✅ Verificación

Cuando el sistema esté funcionando, deberías ver en la consola:

### Si se conecta vía WebSocket:
```
🔧 [Odysee] Iniciando servicio...
✅ [Odysee] Claim ID obtenido: abc123...
🔗 [Odysee] WebSocket conectado
✅ [Odysee] Servicio iniciado (WebSocket)
✅ Conectado a Odysee
```

### Si se conecta vía Polling:
```
🔧 [Odysee] Iniciando servicio...
✅ [Odysee] Claim ID obtenido: abc123...
🔄 [Odysee] Iniciando método de polling...
✅ [Odysee] Servicio iniciado (Polling)
✅ Conectado a Odysee
```

Y cuando lleguen mensajes:
```
💬 [Odysee] Mensaje: Usuario: Hola chat!
```

## 🎨 Personalización

Los usuarios de Odysee aparecerán en el chat con el nombre de usuario. Si quieres cambiar el color o estilo, edita `public/chat.html` y añade:

```css
.username.odysee {
    color: #00D4FF; /* Cambia este color */
}
```

## 🔧 Solución de Problemas

### Error: "Faltan credenciales de Odysee en .env"
- **Solución**: Verifica que al menos una de las variables (`ODYSEE_CHANNEL_NAME` o `ODYSEE_CLAIM_ID`) esté en el `.env` y sin espacios extra

### Error: "No se pudo obtener el claim_id del canal"
- **Solución**: 
  - Verifica que el `ODYSEE_CHANNEL_NAME` sea correcto (sin el @)
  - Asegúrate de que el canal existe en Odysee
  - Intenta usar el `ODYSEE_CLAIM_ID` directamente en su lugar

### Error: "Error obteniendo claim_id"
- **Solución**:
  - Verifica tu conexión a internet
  - Comprueba que la API de Odysee esté disponible
  - Intenta usar el Claim ID directamente en lugar del Channel Name

### El chat no recibe mensajes
- **Solución**:
  - Verifica que haya un stream activo en tu canal de Odysee
  - Comprueba que el Claim ID o Channel Name sea correcto
  - Revisa los logs para ver si hay errores de conexión
  - Asegúrate de que el chat esté habilitado en tu transmisión

### La conexión WebSocket falla
- **Solución**: El sistema cambiará automáticamente a polling. Si persiste el problema:
  - Verifica tu conexión a internet
  - Comprueba que el firewall no esté bloqueando la conexión WebSocket
  - Revisa los logs para más detalles
  - El sistema funcionará con polling como respaldo

### El sistema cambia constantemente entre WebSocket y Polling
- **Solución**:
  - Esto puede indicar problemas de red intermitentes
  - Verifica la estabilidad de tu conexión a internet
  - Revisa los logs para ver los errores específicos
  - El sistema seguirá funcionando con cualquiera de los dos métodos

## 📚 Recursos Adicionales

- [Documentación de Odysee](https://docs.odysee.tv/)
- [API de Odysee (GitHub)](https://github.com/OdyseeTeam/odysee-api)
- [Help Hub de Odysee](https://help.odysee.tv/)

## 🔄 Reconexión Automática

El sistema tiene reconexión automática:
- Si el WebSocket se desconecta, intentará reconectarse después de 5 segundos
- Si el polling falla, reintentará en el siguiente ciclo
- Los mensajes se seguirán recibiendo mientras haya conexión

## 🎯 Notas Importantes

- Odysee no tiene una API pública oficial completa para el chat
- El sistema usa métodos alternativos (WebSocket y polling) para acceder al chat
- La estructura exacta de los mensajes puede variar según la versión de la API de Odysee
- Si la API de Odysee cambia, puede ser necesario actualizar el servicio

## ⚠️ Limitaciones Conocidas

1. **API no oficial**: Odysee no proporciona una API pública oficial para el chat, por lo que el servicio puede necesitar actualizaciones si la estructura de datos cambia.

2. **Requisito de stream activo**: El chat solo está disponible cuando hay una transmisión en vivo activa.

3. **Estructura de mensajes**: La estructura exacta de los mensajes puede variar. Si notas que los mensajes no se muestran correctamente, puede ser necesario ajustar el código de parsing.

---

**¿Necesitas ayuda?** Revisa los logs del sistema para más detalles sobre cualquier error. Si encuentras problemas específicos con la API de Odysee, considera reportarlos en el repositorio del proyecto.

