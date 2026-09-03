## RadioStack

Plataforma modular para gestión de una radio online, basada en Java, Spring Boot y JavaFX.

para la trasminion de radio estoy usando Icecast + BUTT 

### Módulos

- **radiostack-core**: modelo de dominio (DDD ligera), servicios y puertos de repositorio sin dependencias de framework.
- **radiostack-persistence**: implementación de persistencia con Spring Data JPA y PostgreSQL.
- **radiostack-api**: API REST (Spring Boot), autenticación, WebSocket para chat/comentarios en directo y migraciones Flyway.
- **radiostack-admin**: cliente de administración en JavaFX que consume la API.
- **radiostack-stream** (futuro): módulo para integración de streaming de audio.

### Requisitos

- Java 17+
- Maven 3.9+
- PostgreSQL 14+ (configurable en `radiostack-api/src/main/resources/application.yml`)

### Comandos básicos

- Compilar todo: `mvn clean install`
- Ejecutar la API: `cd radiostack-api` y `mvn spring-boot:run`
- Ejecutar el cliente admin (JavaFX): `cd radiostack-admin` y `mvn javafx:run`

### Primer uso

1. Crear base de datos PostgreSQL: `CREATE DATABASE radiostack;` y usuario `radiostack` / contraseña `radiostack` (o ajustar `application.yml`).
2. Arrancar la API; Flyway creará las tablas y un usuario admin por defecto.
3. Login en el cliente admin con **admin@radiostack.local** y la contraseña
   por defecto que fija `DataInitializer` (ver el aviso del paso 4 de la
   guía detallada: hay que cambiarla antes de desplegar en ningún sitio).

### Pasos 1 a 1 para probar desde JavaFX (incluyendo WebSocket)

1. **Preparar la base de datos**
   - Crear la base: `CREATE DATABASE radiostack;`.
   - Crear usuario (ejemplo): `CREATE USER radiostack WITH PASSWORD 'radiostack';`.
   - Dar permisos: `GRANT ALL PRIVILEGES ON DATABASE radiostack TO radiostack;`.
   - Si usas otros datos, ajústalos en `radiostack-api/src/main/resources/application.yml`.

2. **Compilar todo el proyecto**
   - En la raíz (`RadioStack/`): `mvn clean install`.

3. **Arrancar la API (REST + WebSocket)**
   - `cd radiostack-api`
   - `mvn spring-boot:run`
   - La API quedará escuchando en `http://localhost:8080` y expondrá:
     - REST (por ejemplo `GET /api/v1/programas`).
     - WebSocket STOMP en `/ws/chat` (endpoint SockJS) y `/app` como prefijo de aplicación.

4. **Verificar que el usuario admin existe**
   - La primera vez que arranca la API, `DataInitializer` crea una cuenta de
     administración con el correo `admin@radiostack.local` y **una contraseña
     por defecto escrita en el propio código**.
   - Puedes comprobarlo con `POST /api/v1/auth/login` (Postman/curl) o directamente desde el cliente JavaFX (siguiente paso).

   > ⚠️ **Esa contraseña por defecto sirve para arrancar en local y para nada
   > más.** Está en el código fuente, que es público, así que cualquiera la
   > conoce: si este proyecto se despliega en algún sitio accesible desde fuera
   > sin cambiarla antes, la zona de administración queda abierta. Lo pendiente
   > es leerla de una variable de entorno y negarse a arrancar si no está
   > definida, que es lo que hace TaskHub con su semilla de administrador.

5. **Arrancar el cliente JavaFX (interfaz de administración)**
   - En otra terminal:
     - `cd radiostack-admin`
     - `mvn javafx:run`
   - Se abrirá la ventana **RadioStack Admin** con la pantalla de login (tema negro + rojo).

6. **Iniciar sesión desde JavaFX contra la API REST**
   - En la pantalla de login:
     - Email: `admin@radiostack.local`
     - Contraseña: la que fija `DataInitializer` al arrancar por primera vez
   - El cliente JavaFX llamará a `POST /api/v1/auth/login` y, si es correcto, cambiará a la pantalla de **Dashboard**.

7. **Navegar por el Dashboard**
   - En el dashboard verás:
     - Barra superior: **Parrilla**, **Programas**, **Chat en vivo**, **Cerrar sesión**.
     - Mensaje central de bienvenida.

8. **Probar el chat en vivo (WebSocket) desde JavaFX**
   - Necesitas al menos una **emisión** en la base de datos para tener un ID:
     - Opción A: Crear programa y emisión por API (Postman/curl), por ejemplo:
       - `POST /api/v1/programas` con `{"nombre":"Test","descripcion":"","categoria":"","activo":true}` → anotas el `id` del programa.
       - `POST /api/v1/emisiones` con `{"programaId":1,"programaNombre":"Test","diaSemana":"LUNES","horaInicio":"2025-03-01T10:00:00","horaFin":"2025-03-01T12:00:00","estado":"PROGRAMADO"}` → anotas el `id` de la emisión.
     - Opción B: Si ya tienes datos de prueba, usa el ID de cualquier emisión existente.
   - En el cliente JavaFX:
     - Pulsa **Chat en vivo**.
     - En **ID emisión** escribe el ID (ej. `1`).
     - Pulsa **Conectar**. Cuando veas "Conectado a emisión X", el WebSocket STOMP está unido al tópico de esa emisión.
     - Escribe un **alias** y un **mensaje**, luego **Enviar**. El mensaje se envía por WebSocket y aparecerá en la lista (y en cualquier otro cliente conectado al mismo ID).
   - Para probar con dos clientes: abre otra ventana del admin (o otro cliente STOMP) con el mismo ID de emisión; los mensajes se verán en ambos.
   - **Volver al dashboard** cierra la conexión WebSocket y vuelve al panel principal.


---------------------------------------------------------------------------------------------------------------------------------------------------

y de donde saco :



Servidor de streaming (Icecast/SHOUTcast)

Puedes sacar el servidor de streaming de dos sitios: instalándolo tú (software gratis) o usando un servicio que ya lo da (hosting de streaming).

1. Instalarlo tú (Icecast / SHOUTcast)
Icecast es libre y muy usado.
Descarga: https://icecast.org/download/
(Windows, Linux, macOS; en Linux suele estar en los repos: apt install icecast2).
Qué haces: Lo instalas en un equipo que tenga IP pública (tu casa con IP fija, o mejor un VPS).
VPS = servidor alquilado por unos euros al mes (DigitalOcean, Hetzner, OVH, Contabo, etc.). Ahí instalas Icecast y tu radio emite desde esa IP. Luego puedes poner un dominio apuntando a esa IP.
SHOUTcast (después de v2) tiene servidor gratis para uso básico; para más oyentes suelen cobrar.
Descarga: https://shoutcast.com/
Tiene tanto el servidor como opciones de hosting.
Resumen: “De dónde lo sacas” = lo descargas (Icecast) o usas el de SHOUTcast, y lo ejecutas en tu PC o en un VPS.


2. Usar un servicio de streaming (ellos te dan el servidor)
Una empresa ya tiene Icecast/SHOUTcast (o equivalente) y te dan una URL de stream y a veces un panel. Tú solo envías el audio; no instalas nada.
Algunos ejemplos (hay muchos más):
Servicio	Qué te dan	Precio aproximado
Radio.co	Stream URL, panel, estadísticas	Planes desde ~$/month
Live365	Streaming + licencias (EE.UU.)	Planes de pago
StreamGuys	Infraestructura profesional	Bajo demanda
Azuracast	Software gratis, puedes autoalojarlo o usar quien lo ofrezca	Gratis (si lo instalas tú)
También hay radios online tipo “crea tu radio en 5 minutos” que por detrás usan streaming; suelen incluir reproductor y a veces dominio/subdominio.
Resumen: “De dónde lo sacas” = contratas un hosting de streaming y ellos te dan la URL (ej. https://stream.radio.co/xxxx) y a veces el dominio o subdominio.


Qué elegir
Quieres control total y no pagar por el servidor:
Instala Icecast en un VPS (5–10 €/mes) y opcionalmente un dominio.
Quieres algo rápido y que alguien lo mantenga:
Contrata un servicio de streaming (Radio.co, Live365, etc.); te dan la URL de stream y a veces web/reproductor.
En ambos casos, RadioStack (tu proyecto) puede seguir siendo tu “cerebro”: parrilla, programas, chat, etc. El stream en sí lo pone Icecast/SHOUTcast, ya sea el que tú instalas o el que te da el servicio.