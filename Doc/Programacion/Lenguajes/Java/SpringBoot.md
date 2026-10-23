Fase 3 — Java avanzado
Bloque 24: Spring Boot — IoC, inyección de dependencias y contenedor
Spring Boot facilita la creación de aplicaciones Java mediante Spring Framework, que gestiona objetos, dependencias y configuración para reducir el código repetitivo.
1. ¿Qué es IoC?
IoC (Inversion of Control) es un principio por el que una clase deja de controlar directamente la creación y gestión de sus dependencias: esa responsabilidad se delega a otro componente, en este caso, al contenedor de Spring.
Sin IoC, una clase podría crear sus propias dependencias:
public class PedidoService {
    private final PedidoRepository repository =
        new PedidoRepository();
}
Problemas:
    • PedidoService queda acoplado a una implementación concreta.
    • Sustituir el repositorio por un mock para realizar pruebas resulta más difícil.
    • La creación de dependencias queda repartida por el código.
2. Inyección de dependencias (DI)
La inyección de dependencias es una forma de aplicar IoC: las dependencias se proporcionan desde fuera, en lugar de crearse dentro de la clase.
@Service
public class PedidoService {

    private final PedidoRepository repository;

    public PedidoService(PedidoRepository repository) {
        this.repository = repository;
    }
}
Spring detecta los componentes registrados, crea sus instancias y proporciona el repositorio al construir PedidoService.
Esta técnica reduce el acoplamiento y facilita las pruebas.
3. ¿Qué es el contenedor de Spring?
El contenedor es responsable de crear, configurar y gestionar los objetos que Spring conoce como beans.
Por ejemplo:
@Repository
public class PedidoRepository {
    // Acceso a datos
}
@Service
public class PedidoService {
    private final PedidoRepository repository;

    public PedidoService(PedidoRepository repository) {
        this.repository = repository;
    }
}
@SpringBootApplication
public class Aplicacion {
    public static void main(String[] args) {
        SpringApplication.run(Aplicacion.class, args);
    }
}
@SpringBootApplication activa, entre otras cosas, la configuración automática y el escaneo de componentes desde el paquete de la clase principal y sus subpaquetes.
Spring registra el repositorio y el servicio como beans, siempre que estén dentro del alcance del escaneo y no haya otros problemas de configuración.
4. Anotaciones fundamentales
Anotación
Función habitual
@Component
Registra un componente gestionado por Spring.
@Service
Identifica un componente de lógica de negocio.
@Repository
Identifica un componente de acceso a datos.
@Controller
Define un controlador MVC.
@RestController
Define un controlador que devuelve directamente datos en la respuesta HTTP.
@Configuration
Declara una clase de configuración.
@Bean
Registra como bean el objeto devuelto por un método.
@Service y @Repository son especializaciones de @Component; aportan intención semántica y, en el caso de @Repository, pueden participar en la traducción de excepciones de persistencia.
5. ¿Por qué preferir la inyección por constructor?
Es la opción recomendada para dependencias obligatorias:
@Service
public class PagoService {

    private final PasarelaPago pasarela;

    public PagoService(PasarelaPago pasarela) {
        this.pasarela = pasarela;
    }
}
Ventajas:
    • Las dependencias son explícitas.
    • Los campos pueden ser final.
    • Puedes crear el objeto directamente en un test.
    • El objeto no queda construido sin sus dependencias obligatorias.
Si una clase tiene un único constructor, Spring normalmente no necesita que lo marques con @Autowired.
Pregunta de comprobación
¿Cuál es la diferencia entre IoC e inyección de dependencias?
A. Son conceptos completamente independientes y no tienen relación.
B. IoC es el principio de delegar el control; la inyección de dependencias es una técnica para aplicarlo.
C. IoC sirve únicamente para conectarse a bases de datos.
D. La inyección de dependencias significa que una clase debe crear sus propios objetos.
Comprobar
Correcto.
La respuesta es B. IoC es el principio general de invertir quién controla la creación o el flujo de ejecución; DI es una técnica mediante la que las dependencias se proporcionan a los objetos desde fuera.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 25: Beans y ciclo de vida
Un bean es un objeto cuya creación y gestión está controlada por el contenedor de Spring. Spring puede instanciarlo, inyectarle dependencias, ejecutar métodos de inicialización y destruirlo cuando se cierra el contexto.
1. ¿Cómo se registra un bean?
Hay dos formas habituales.
Mediante anotaciones:
@Service
public class UsuarioService {
}
Spring detecta la clase durante el escaneo de componentes y registra un bean.
Mediante @Bean:
@Configuration
public class AppConfig {

    @Bean
    public DateTimeFormatter dateFormatter() {
        return DateTimeFormatter.ISO_LOCAL_DATE;
    }
}
Esta segunda opción resulta útil cuando quieres controlar la construcción de un objeto, especialmente si su clase pertenece a una biblioteca externa que no puedes modificar.
2. Ciclo de vida de un bean
De forma simplificada, el ciclo de vida habitual es:
1. Instanciación
Spring crea el objeto.
2. Inyección de dependencias
Se proporcionan sus dependencias.
3. Inicialización
Se ejecutan los callbacks de inicialización.
4. Uso
El bean está disponible para la aplicación.
5. Destrucción
Se ejecuta la limpieza cuando corresponde.
El ciclo real incluye más pasos, como los BeanPostProcessors, que permiten modificar o envolver beans, por ejemplo mediante proxies.
3. Inicialización y destrucción
Puedes utilizar @PostConstruct y @PreDestroy para ejecutar tareas en momentos concretos:
@Component
public class CacheService {

    @PostConstruct
    public void inicializar() {
        System.out.println("Inicializando caché");
    }

    @PreDestroy
    public void cerrar() {
        System.out.println("Liberando recursos");
    }
}
    • @PostConstruct: se ejecuta después de que Spring haya realizado la inyección de dependencias y antes de que el bean se considere inicializado por completo.
    • @PreDestroy: se ejecuta durante la destrucción gestionada del bean.
En Java moderno, estas anotaciones pertenecen a jakarta.annotation, habitual en Spring Boot 3 y posteriores.
Precaución: evita realizar tareas lentas o bloqueantes durante la inicialización sin una razón clara, porque pueden retrasar el arranque de la aplicación.
4. Scope: ¿cuántas instancias se crean?
El scope define cómo se crean y comparten las instancias de un bean.
Scope
Comportamiento
singleton
Una instancia por contenedor de Spring; es el scope predeterminado.
prototype
Spring crea una instancia nueva cada vez que solicita el bean.
request
Una instancia por petición HTTP, en aplicaciones web compatibles.
session
Una instancia por sesión HTTP.
Ejemplo:
@Component
@Scope("prototype")
public class GeneradorInforme {
}
No confundas singleton de Spring con el patrón Singleton de Java: Spring mantiene una instancia por contenedor, pero no impide que el código cree otras instancias directamente.
Además, los beans singleton suelen compartirse entre peticiones concurrentes. Por eso, es recomendable que sean sin estado mutable por petición o que gestionen la concurrencia correctamente.
Pregunta de comprobación
Un servicio anotado con @Service tiene un campo mutable que guarda el identificador del usuario que está atendiendo. ¿Qué problema puede aparecer si el bean utiliza el scope predeterminado?
A. Spring crea automáticamente un servicio distinto para cada petición.
B. El campo mutable puede compartirse entre peticiones concurrentes y provocar condiciones de carrera o mezclar datos de usuarios.
C. @Service impide que sus campos puedan modificarse.
D. El bean se destruye después de cada método invocado.
Comprobar
Correcto.
La respuesta es B. El scope predeterminado es singleton, por lo que el servicio se comparte entre peticiones. El estado específico de cada usuario debe mantenerse normalmente en variables locales o en mecanismos adecuados para ese contexto, no en campos mutables compartidos.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 26: Configuración y perfiles
Spring Boot permite separar la configuración del código para adaptar una aplicación a distintos entornos, como desarrollo, pruebas y producción, sin tener que modificar las clases Java.
1. application.properties y application.yml
La configuración habitual se encuentra en src/main/resources/application.properties o application.yml.
Por ejemplo, en application.properties:
spring.application.name=taskhub
server.port=8081

spring.datasource.url=${DB_URL}
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
Las expresiones ${DB_URL}, ${DB_USER} y ${DB_PASSWORD} permiten obtener valores desde variables de entorno u otras fuentes de configuración admitidas por Spring Boot.
También puedes escribir la configuración en YAML:
spring:
  application:
    name: taskhub
  datasource:
    url: ${DB_URL}
    username: ${DB_USER}
    password: ${DB_PASSWORD}

server:
  port: 8081
Ambos formatos son válidos. No necesitas utilizar los dos simultáneamente.
2. Perfiles de Spring
Los perfiles permiten activar configuraciones específicas para cada entorno.
Por ejemplo, crea estos archivos:
application-dev.properties
server.port=8081
app.modo=desarrollo
application-prod.properties
server.port=8080
app.modo=produccion
Puedes activar un perfil mediante una propiedad de configuración:
spring.profiles.active=dev
O al arrancar la aplicación:
java -jar app.jar --spring.profiles.active=prod
De esta manera, la misma aplicación puede utilizar configuraciones diferentes según el entorno.
Importante: evita fijar dev como perfil activo en el archivo de configuración común si esperas que cada entorno decida cuál utilizar. En despliegues reales suele ser preferible seleccionar el perfil externamente.
3. Configuración tipada con @ConfigurationProperties
Si tienes varias propiedades relacionadas, puedes agruparlas en una clase tipada en vez de leerlas individualmente con @Value.
@ConfigurationProperties(prefix = "app")
public record AppProperties(
    String modo,
    int maxIntentos
) {}
Configuración:
app.modo=desarrollo
app.max-intentos=3
Para registrar esta configuración, puedes habilitar el escaneo:
@SpringBootApplication
@ConfigurationPropertiesScan
public class Aplicacion {
    public static void main(String[] args) {
        SpringApplication.run(Aplicacion.class, args);
    }
}
Spring vinculará las propiedades con los componentes del record.
Esta alternativa aporta tipado, facilita agrupar propiedades relacionadas y permite añadir validación mediante anotaciones cuando corresponda.
4. Configuración por entorno y seguridad
Buenas prácticas:
    • No guardar contraseñas, tokens o claves privadas en el repositorio.
    • Utilizar variables de entorno o un gestor de secretos para valores sensibles.
    • Mantener valores predeterminados seguros.
    • No confundir perfiles con mecanismos de seguridad: activar prod no protege por sí mismo la aplicación.
    • Validar las propiedades críticas al arrancar para detectar errores de configuración cuanto antes.
Pregunta de comprobación
Necesitas desplegar la misma aplicación en desarrollo y producción, cambiando el puerto y la configuración de la base de datos. ¿Cuál es el enfoque más adecuado?
A. Mantener dos versiones diferentes del código Java para cada entorno.
B. Utilizar perfiles y propiedades externas, guardando las credenciales fuera del repositorio.
C. Escribir las contraseñas directamente en las clases Java.
D. Cambiar manualmente el código cada vez que se despliega.
Comprobar
Correcto.
La respuesta es B. Los perfiles permiten separar configuraciones por entorno y las propiedades externas evitan acoplar el código a valores específicos del despliegue. Las credenciales deben gestionarse fuera del repositorio.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 27: Controllers, Services y Repositories
En una API Spring Boot es habitual separar el código en tres capas. Cada una tiene una responsabilidad concreta y delega el trabajo que no le corresponde a la siguiente.
Controller
HTTP · Recibe peticiones y devuelve respuestas
Service
Negocio · Aplica reglas y coordina operaciones
Repository
Persistencia · Consulta y modifica los datos
Base de datos
1. Repository: acceso a datos
Con Spring Data JPA, normalmente no necesitas implementar manualmente las operaciones CRUD básicas.
public interface UsuarioRepository
        extends JpaRepository<Usuario, Long> {
    Optional<Usuario> findByEmail(String email);
}
Spring genera una implementación del repositorio. Puedes utilizar métodos heredados como findById(), findAll(), save() y deleteById().
También puede generar consultas a partir de nombres de métodos, como findByEmail().
2. Service: lógica de negocio
El servicio contiene las reglas de la aplicación y utiliza el repositorio para acceder a los datos.
@Service
public class UsuarioService {

    private final UsuarioRepository repository;

    public UsuarioService(UsuarioRepository repository) {
        this.repository = repository;
    }

    public Usuario buscarPorId(Long id) {
        return repository.findById(id)
            .orElseThrow(() ->
                new UsuarioNoEncontradoException(id));
    }
}
En este ejemplo, el servicio decide qué hacer cuando el usuario no existe. La excepción es una excepción de dominio que tendría que definirse en el proyecto.
En aplicaciones reales, el servicio también puede coordinar varios repositorios, aplicar reglas de negocio y gestionar transacciones.
3. Controller: entrada HTTP
El controlador expone la operación mediante una API REST.
@RestController
@RequestMapping("/usuarios")
public class UsuarioController {

    private final UsuarioService service;

    public UsuarioController(UsuarioService service) {
        this.service = service;
    }

    @GetMapping("/{id}")
    public Usuario buscar(@PathVariable Long id) {
        return service.buscarPorId(id);
    }
}
Una petición GET /usuarios/5 provoca este flujo:
    1. Spring dirige la petición al método del controlador.
    2. El controlador obtiene el identificador de la URL.
    3. El servicio ejecuta la operación de negocio.
    4. El repositorio consulta la base de datos.
    5. Spring convierte el objeto devuelto en JSON y construye la respuesta HTTP.
El código anterior es ilustrativo: en una API completa suele ser preferible devolver un DTO en lugar de exponer directamente la entidad JPA.
4. ¿Por qué separar las capas?
    • Mantenibilidad: cada capa tiene una responsabilidad delimitada.
    • Testing: puedes probar el servicio con un repositorio simulado.
    • Reutilización: varios controladores pueden utilizar el mismo servicio.
    • Menor acoplamiento: los controladores no necesitan conocer los detalles de persistencia.
Una regla práctica: evita introducir la lógica de negocio en el controlador y evita que el repositorio se convierta en el lugar donde se decide el comportamiento de la aplicación.
Pregunta de comprobación
Necesitas implementar una regla de negocio que impida eliminar un usuario que tenga pedidos pendientes. ¿Dónde debería residir principalmente esa regla?
A. En el Controller, porque recibe la petición HTTP.
B. En el Service, que aplica la regla de negocio y coordina los repositorios necesarios.
C. En el Repository, porque toda regla de negocio es una consulta SQL.
D. En application.properties, porque es configuración.
Comprobar
Correcto.
La respuesta es B. El servicio debe comprobar la regla de negocio y coordinar el acceso a los datos. El controlador gestiona HTTP y el repositorio se ocupa de la persistencia.
Continuar con Spring Boot
Fase 3 — Spring Boot
Bloque 28: Inyección por constructor
La inyección por constructor consiste en proporcionar las dependencias de una clase mediante su constructor, en lugar de crearlas dentro de ella o asignarlas mediante setters.
En Spring Boot es la opción recomendada para las dependencias obligatorias.
1. Inyección por constructor frente a creación manual
Una implementación con alto acoplamiento:
@Service
public class PedidoService {

    private final PedidoRepository repository =
        new PedidoRepository();
}
Problemas: el servicio decide cómo crear el repositorio, queda ligado a una implementación concreta y dificulta sustituir esa dependencia en los tests.
La versión recomendada:
@Service
public class PedidoService {

    private final PedidoRepository repository;

    public PedidoService(PedidoRepository repository) {
        this.repository = repository;
    }
}
Spring proporciona el repositorio cuando crea el servicio.
2. ¿Por qué usar un constructor?
    • Dependencias obligatorias: el objeto no puede construirse correctamente sin ellas.
    • Inmutabilidad: puedes declarar las referencias como final.
    • Testing sencillo: puedes pasar un mock o una implementación alternativa directamente.
    • Menos acoplamiento: la clase depende de una abstracción y no tiene que construir su implementación.
Por ejemplo, si PedidoRepository es una interfaz, puedes proporcionar distintas implementaciones según el contexto.
3. ¿Es necesario @Autowired?
Cuando una clase tiene un único constructor, Spring lo utiliza automáticamente:
@Service
public class PedidoService {

    private final PedidoRepository repository;

    @Autowired // Opcional si este es el único constructor
    public PedidoService(PedidoRepository repository) {
        this.repository = repository;
    }
}
No necesitas @Autowired en ese caso.
Si existen varios constructores, debes indicar claramente cuál debe utilizar Spring, por ejemplo, mediante @Autowired, o proporcionar una configuración apropiada.
4. ¿Qué ocurre con Lombok?
Si el proyecto utiliza Lombok, puedes reducir código repetitivo:
@Service
@RequiredArgsConstructor
public class PedidoService {
    private final PedidoRepository repository;
    private final NotificacionService notificaciones;
}
@RequiredArgsConstructor genera un constructor para los campos final y los campos marcados como @NonNull que lo requieran. Spring puede utilizar ese constructor sin necesidad de añadir @Autowired.
Lombok es opcional: la misma arquitectura puede implementarse escribiendo el constructor manualmente.
5. ¿Cuándo evitar la inyección por campos?
@Autowired
private PedidoRepository repository;
Aunque funciona en Spring, tiene desventajas: la dependencia no queda explícita en el constructor, la clase resulta más difícil de instanciar directamente en tests y no puedes declarar ese campo final.
Regla práctica: utiliza inyección por constructor para dependencias obligatorias. Si una clase necesita demasiadas dependencias, considera si está asumiendo demasiadas responsabilidades.
Pregunta de comprobación
¿Por qué es preferible la inyección por constructor para una dependencia obligatoria?
A. Porque permite que Spring cree automáticamente cualquier clase, aunque no esté registrada.
B. Porque hace explícita la dependencia, permite usar campos final y facilita las pruebas.
C. Porque elimina la necesidad de interfaces y repositorios.
D. Porque obliga a que todos los métodos de la clase sean estáticos.
Comprobar
Correcto.
La respuesta es B. El constructor declara qué necesita la clase para funcionar, permite asignar las dependencias a campos final y facilita proporcionar mocks durante las pruebas.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 29: DTOs, validación y manejo global de errores
En una API REST no conviene exponer directamente las entidades de base de datos. Los DTOs (Data Transfer Objects) permiten definir qué datos recibe y devuelve la API, mientras que la validación y el manejo global de errores hacen que las respuestas sean consistentes.
1. DTOs: separar la API de las entidades
Imagina que tienes una entidad Usuario con id, nombre, email y passwordHash. No quieres exponer la contraseña cifrada en las respuestas.
Puedes definir un DTO de respuesta:
public record UsuarioResponse(
    Long id,
    String nombre,
    String email
) {}
Y otro para recibir los datos de creación:
public record CrearUsuarioRequest(
    String nombre,
    String email,
    String password
) {}
Así controlas los campos de entrada y salida por separado. La entidad JPA puede tener otros campos y relaciones que no necesitas exponer.
2. Validación con Jakarta Validation
Añade restricciones al DTO de entrada:
public record CrearUsuarioRequest(
    @NotBlank
    @Size(max = 80)
    String nombre,

    @NotBlank
    @Email
    String email,

    @NotBlank
    @Size(min = 12, max = 72)
    String password
) {}
Para utilizar estas anotaciones en Spring Boot, necesitas tener disponible la dependencia de validación, normalmente spring-boot-starter-validation.
En el controlador, activa la validación con @Valid:
@PostMapping("/usuarios")
public ResponseEntity<UsuarioResponse> crear(
        @Valid @RequestBody CrearUsuarioRequest request) {

    UsuarioResponse usuario = service.crear(request);

    return ResponseEntity
        .status(HttpStatus.CREATED)
        .body(usuario);
}
Si la petición incumple las restricciones, Spring puede rechazarla antes de ejecutar el cuerpo del método.
Importante: la validación de los campos no sustituye a la lógica de negocio. Por ejemplo, comprobar que un email tenga un formato válido no garantiza que no esté ya registrado.
3. Manejo global de errores
Sin un tratamiento uniforme, distintos controladores pueden devolver respuestas de error diferentes. @RestControllerAdvice permite centralizar ese comportamiento.
Podemos definir una respuesta de error:
public record ApiError(
    int status,
    String mensaje
) {}
Y gestionar errores de validación globalmente:
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiError> handleValidation(
            MethodArgumentNotValidException ex) {

        ApiError error = new ApiError(
            400,
            "La petición contiene datos inválidos"
        );

        return ResponseEntity
            .badRequest()
            .body(error);
    }
}
Este ejemplo devuelve un mensaje general. En una API real puedes incluir los campos que han fallado, pero evita devolver trazas internas, contraseñas o información sensible.
También puedes gestionar excepciones de negocio:
@ExceptionHandler(UsuarioNoEncontradoException.class)
public ResponseEntity<ApiError> handleNotFound(
        UsuarioNoEncontradoException ex) {

    ApiError error = new ApiError(404, ex.getMessage());

    return ResponseEntity
        .status(HttpStatus.NOT_FOUND)
        .body(error);
}
La excepción UsuarioNoEncontradoException sería una excepción propia definida por la aplicación.
4. Códigos HTTP habituales
Código
Significado
Ejemplo
200 OK
Operación correcta
Consultar un usuario
201 Created
Recurso creado
Crear un usuario
400 Bad Request
Petición inválida
Fallo de validación
401 Unauthorized
Autenticación ausente o inválida
Token inválido
403 Forbidden
Sin permisos suficientes
Usuario sin autorización
404 Not Found
Recurso no encontrado
Usuario inexistente
409 Conflict
Conflicto con el estado actual
Email duplicado
500 Internal Server Error
Error inesperado del servidor
Fallo no controlado
Criterio profesional: utiliza DTOs para delimitar el contrato de la API, valida las entradas en los límites del sistema y centraliza la traducción de excepciones a respuestas HTTP.
Pregunta de comprobación
Un cliente envía una petición para crear un usuario con un email que no cumple @Email. El controlador utiliza @Valid. ¿Qué debería suceder?
A. Spring debería rechazar la entrada por validación y devolver normalmente un error 400.
B. La petición debería crear el usuario igualmente y corregir el email automáticamente.
C. Debe devolverse siempre un 500, porque toda validación es un error interno.
D. @Valid valida automáticamente si el email ya existe en la base de datos.
Comprobar
Correcto.
La respuesta es A. Con la dependencia de validación configurada, @Valid hace que Spring compruebe las restricciones del DTO. Si falla la validación de la petición, lo habitual es responder con HTTP 400. La unicidad del email requiere una comprobación adicional de negocio y persistencia.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 30: APIs REST y códigos HTTP
Una API REST permite que distintos sistemas se comuniquen mediante HTTP, intercambiando recursos y representaciones, habitualmente en JSON.
En Spring Boot, normalmente expones estos recursos mediante controladores con @RestController.
1. Diseñar endpoints REST
Los endpoints deben representar recursos, utilizando los métodos HTTP para expresar la operación.
Método
Endpoint
Operación
GET
/usuarios
Listar usuarios
GET
/usuarios/15
Consultar un usuario
POST
/usuarios
Crear un usuario
PUT
/usuarios/15
Reemplazar un usuario
PATCH
/usuarios/15
Modificar parcialmente un usuario
DELETE
/usuarios/15
Eliminar un usuario
Es preferible utilizar sustantivos como /usuarios en lugar de rutas como /obtenerUsuarios.
2. Implementar un controlador REST
Ejemplo de un controlador sencillo:
@RestController
@RequestMapping("/usuarios")
public class UsuarioController {

    private final UsuarioService service;

    public UsuarioController(UsuarioService service) {
        this.service = service;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UsuarioResponse> obtener(
            @PathVariable Long id) {

        UsuarioResponse usuario = service.obtenerPorId(id);

        return ResponseEntity.ok(usuario);
    }

    @PostMapping
    public ResponseEntity<UsuarioResponse> crear(
            @Valid @RequestBody CrearUsuarioRequest request) {

        UsuarioResponse creado = service.crear(request);

        return ResponseEntity
            .status(HttpStatus.CREATED)
            .body(creado);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> eliminar(@PathVariable Long id) {
        service.eliminar(id);
        return ResponseEntity.noContent().build();
    }
}
Anotaciones importantes:
    • @RestController: indica que la clase expone endpoints y devuelve datos en la respuesta HTTP.
    • @RequestMapping: define una ruta base.
    • @GetMapping, @PostMapping y @DeleteMapping: asocian métodos Java con métodos HTTP.
    • @PathVariable: obtiene un valor de la ruta, como el id.
    • @RequestBody: convierte el cuerpo JSON de la petición en un objeto Java.
    • ResponseEntity: permite controlar el estado HTTP y el cuerpo de la respuesta.
El servicio se encarga de la lógica de negocio. El controlador recibe la petición y coordina la respuesta.
3. Elegir correctamente los códigos HTTP
Una API no debería responder siempre con 200 OK. El estado debe representar el resultado de la operación.
Situación
Código habitual
Consulta correcta
200 OK
Creación correcta
201 Created
Eliminación correcta sin cuerpo
204 No Content
Datos de entrada inválidos
400 Bad Request
Usuario no autenticado
401 Unauthorized
Usuario sin permisos
403 Forbidden
Recurso inexistente
404 Not Found
Conflicto, como un email duplicado
409 Conflict
Error inesperado del servidor
500 Internal Server Error
También conviene conocer dos propiedades importantes de los métodos HTTP:
    • Seguro: la operación no pretende modificar el estado del servidor. Por ejemplo, GET.
    • Idempotente: repetir la misma petición produce el mismo efecto final que ejecutarla una sola vez. PUT y DELETE están definidos como idempotentes, aunque las respuestas concretas puedan variar.
POST no es idempotente por defecto: repetir una petición de creación podría crear varios recursos.
Pregunta de comprobación
Una API recibe DELETE /usuarios/15. El usuario existe y se elimina correctamente. No se necesita devolver ningún cuerpo en la respuesta. ¿Qué respuesta es la más apropiada?
A. 200 OK siempre, aunque no se devuelva contenido.
B. 201 Created, porque la operación terminó correctamente.
C. 204 No Content, porque la eliminación se completó sin cuerpo de respuesta.
D. 404 Not Found, porque el recurso ya no existe después de eliminarlo.
Comprobar
Correcto.
La respuesta es C. 204 No Content indica que la operación se completó correctamente y que la respuesta no contiene un cuerpo. En Spring Boot se puede expresar con ResponseEntity.noContent().build().
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 31: JPA/Hibernate, entidades y relaciones
JPA es la especificación de Java que define cómo mapear objetos Java a bases de datos relacionales. Hibernate es una de sus implementaciones más utilizadas.
Spring Data JPA facilita todavía más el acceso a los datos mediante repositorios.
La idea central es el ORM (Object-Relational Mapping): representar filas de una tabla mediante objetos Java.
1. Crear una entidad
Supongamos que tenemos una tabla usuarios. Podemos representarla así:
import jakarta.persistence.*;

@Entity
@Table(name = "usuarios")
public class Usuario {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    protected Usuario() {}

    public Usuario(String email) {
        this.email = email;
    }

    public Long getId() {
        return id;
    }

    public String getEmail() {
        return email;
    }
}
Anotaciones importantes:
    • @Entity: declara que la clase se mapea a una entidad persistente.
    • @Table: permite especificar el nombre de la tabla.
    • @Id: identifica la clave primaria.
    • @GeneratedValue: configura la generación del identificador.
    • @Column: permite definir restricciones y características de una columna.
    • El constructor sin argumentos protected permite a JPA instanciar la entidad.
Importante: unique = true define una restricción de unicidad en el esquema cuando este se genera o actualiza según la configuración. No sustituye el tratamiento de errores de duplicidad en la aplicación.
2. Relaciones entre entidades
Las relaciones de una base de datos se representan mediante anotaciones JPA.
Tipos principales de relaciones
@ManyToOne — Muchos a uno
Muchos pedidos pertenecen a un mismo usuario. La clave foránea suele estar en la tabla de pedidos.
@OneToMany — Uno a muchos
Un usuario puede tener varios pedidos. Suele ser el lado inverso de la relación anterior.
@OneToOne — Uno a uno
Por ejemplo, un usuario tiene un perfil único.
@ManyToMany — Muchos a muchos
Por ejemplo, varios estudiantes pueden estar matriculados en varias asignaturas. Normalmente se utiliza una tabla intermedia.
3. Ejemplo: usuario y pedidos
Un usuario puede tener muchos pedidos y cada pedido pertenece a un usuario.
@Entity
public class Pedido {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "usuario_id", nullable = false)
    private Usuario usuario;

    protected Pedido() {}
}
Aquí:
    • @ManyToOne expresa la relación entre pedidos y usuario.
    • @JoinColumn define la columna que almacena la clave foránea.
    • FetchType.LAZY permite aplazar la carga de la entidad relacionada hasta que se necesite, siempre que el contexto de persistencia permita acceder a ella.
En el lado @OneToMany, si lo añadiéramos a Usuario, podríamos usar mappedBy = "usuario" para indicar que la relación la controla el atributo usuario de Pedido.
No conviene añadir relaciones bidireccionales por defecto: pueden complicar la serialización JSON, las consultas y la gestión de entidades.
4. ¿Cómo se guardan los datos?
Con Spring Data JPA puedes definir un repositorio sin escribir manualmente las operaciones CRUD:
public interface UsuarioRepository
        extends JpaRepository<Usuario, Long> {
}
Y usarlo desde un servicio:
@Service
public class UsuarioService {

    private final UsuarioRepository repository;

    public UsuarioService(UsuarioRepository repository) {
        this.repository = repository;
    }

    public Usuario guardar(Usuario usuario) {
        return repository.save(usuario);
    }
}
save() permite guardar una entidad nueva o actualizar una existente según cómo JPA determine su estado. No significa necesariamente que cada llamada ejecute inmediatamente un INSERT o UPDATE: los cambios pueden sincronizarse con la base de datos durante el flush o la confirmación de la transacción.
Pregunta de comprobación
Tenemos una entidad Pedido con una referencia a Usuario. Un usuario puede tener muchos pedidos, pero cada pedido pertenece a un solo usuario. ¿Qué anotación corresponde al atributo usuario de Pedido?
A. @OneToOne
B. @ManyToOne
C. @ManyToMany
D. @OneToMany
Comprobar
Correcto.
La respuesta es B: @ManyToOne. Muchos pedidos pueden referenciar al mismo usuario. En la base de datos, lo habitual es que cada pedido almacene la clave foránea usuario_id.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 32: Consultas, paginación y problema N+1 en JPA/Hibernate
En aplicaciones reales, no basta con guardar y recuperar entidades. También necesitas consultar datos eficientemente, devolver resultados paginados y evitar consultas SQL innecesarias.
1. Crear consultas con Spring Data JPA
Spring Data JPA puede generar consultas a partir del nombre de los métodos del repositorio.
public interface UsuarioRepository
        extends JpaRepository<Usuario, Long> {

    Optional<Usuario> findByEmail(String email);

    List<Usuario> findByActivoTrue();

    boolean existsByEmail(String email);
}
Por ejemplo, findByEmail() busca por el campo email, mientras que existsByEmail() permite comprobar si existe un usuario con ese correo.
Para consultas más específicas, puedes utilizar @Query:
@Query("SELECT u FROM Usuario u WHERE u.activo = true")
List<Usuario> buscarActivos();
Esta consulta utiliza JPQL, que trabaja con entidades y atributos Java, en lugar de nombres de tablas y columnas SQL.
2. Paginación y ordenación
Si una tabla contiene cientos de miles de usuarios, devolverlos todos en una sola petición puede consumir mucha memoria y generar respuestas lentas.
Spring Data permite paginar mediante Pageable:
@GetMapping
public Page<UsuarioResponse> listar(
        @PageableDefault(size = 20, sort = "email")
        Pageable pageable) {

    return service.listar(pageable);
}
En el servicio:
public Page<UsuarioResponse> listar(Pageable pageable) {
    return repository.findAll(pageable)
            .map(this::toResponse);
}
Una petición podría ser:
GET /usuarios?page=0&size=20&sort=email,asc
Conceptos importantes:
    • Pageable: especifica página, tamaño y ordenación.
    • Page<T>: incluye los elementos y metadatos como el total de resultados y páginas.
    • Slice<T>: permite saber si existe otra porción de resultados, sin necesitar necesariamente el recuento total.
    • La primera página es la 0.
La paginación reduce los resultados devueltos, aunque no garantiza por sí sola que cualquier consulta sea rápida. El diseño de la consulta y los índices siguen siendo importantes.
3. El problema N+1
Es un problema frecuente al trabajar con relaciones entre entidades.
Imagina que recuperas 100 pedidos y después accedes al usuario asociado a cada pedido. Si la relación es LAZY, Hibernate podría ejecutar:
    1. Una consulta para recuperar los 100 pedidos.
    2. Una consulta adicional para cargar el usuario de cada pedido.
En el peor caso, serían 101 consultas SQL: una inicial más 100 consultas adicionales.
Comparación conceptual
Sin optimizar
N+1
1 consulta para pedidos + N consultas para usuarios.
100 pedidos → hasta 101 consultas
Con carga planificada
Menos consultas
Recuperar pedidos y usuarios relacionados en una consulta apropiada, cuando sea posible.
100 pedidos → por ejemplo, 1 consulta JOIN
Una solución posible es JOIN FETCH:
@Query("""
    SELECT p
    FROM Pedido p
    JOIN FETCH p.usuario
    """)
List<Pedido> buscarConUsuario();
Así se solicitan los pedidos junto con sus usuarios en la misma consulta SQL.
Matiz importante: no conviene aplicar JOIN FETCH indiscriminadamente. Combinarlo con colecciones y paginación puede producir duplicados, grandes cantidades de datos o resultados de paginación incorrectos. Otras opciones son @EntityGraph, proyecciones DTO o consultas específicas.
La estrategia correcta depende de qué datos necesita realmente la operación.
Pregunta de comprobación
Un endpoint recupera 100 pedidos y, al acceder a pedido.getUsuario(), Hibernate ejecuta una consulta adicional por cada pedido. ¿Qué problema estás observando?
A. Una transacción distribuida.
B. El problema N+1, que puede reducirse planificando la carga de las relaciones.
C. Un error de inyección de dependencias.
D. Un problema de validación de DTOs.
Comprobar
Correcto.
La respuesta es B. Se ejecuta una consulta inicial y después una por cada relación accedida. Puedes evaluar JOIN FETCH, @EntityGraph o proyecciones para evitar consultas innecesarias.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 33: Transacciones y propagation
Una transacción agrupa varias operaciones en una unidad de trabajo. Su objetivo es que los cambios se confirmen correctamente o se reviertan cuando se produce un fallo que debe provocar rollback.
En Spring Boot se suelen gestionar mediante @Transactional.
1. ¿Qué es una transacción?
Imagina que una operación transfiere dinero entre dos cuentas:
    1. Restar 100 € de la cuenta A.
    2. Sumar 100 € a la cuenta B.
Si se resta el dinero, pero falla el ingreso, los datos quedarían inconsistentes. Ambas operaciones deben formar parte de una misma transacción.
@Service
public class TransferenciaService {

    private final CuentaRepository repository;

    public TransferenciaService(CuentaRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public void transferir(Long origen, Long destino, BigDecimal importe) {
        Cuenta cuentaOrigen = repository.findById(origen).orElseThrow();
        Cuenta cuentaDestino = repository.findById(destino).orElseThrow();

        cuentaOrigen.retirar(importe);
        cuentaDestino.ingresar(importe);
    }
}
Si la operación termina correctamente, Spring confirma la transacción. Si se produce una excepción que activa el rollback, se revierten los cambios transaccionales.
Por defecto, Spring provoca rollback ante excepciones RuntimeException y Error, pero no ante todas las excepciones comprobadas (checked exceptions). Puedes configurar el comportamiento, por ejemplo, con rollbackFor.
2. ¿Qué significa propagation?
La propagación define cómo se comporta un método transaccional cuando ya existe una transacción.
Los dos modos más importantes para empezar son:
Propagation.REQUIRED
Por defecto
Si ya existe una transacción, se une a ella. Si no existe, crea una nueva.
Es la opción habitual para operaciones de negocio.
Propagation.REQUIRES_NEW
Siempre utiliza una transacción independiente y suspende temporalmente la transacción exterior, si la hay.
Puede ser útil para registrar ciertos resultados de auditoría por separado, teniendo en cuenta que la transacción exterior podría revertirse mientras la interior ya se ha confirmado.
Ejemplo:
@Transactional
public void procesarPedido() {
    guardarPedido();       // REQUIRED: comparte la transacción
    registrarAuditoria(); // REQUIRES_NEW: transacción independiente
}
Si registrarAuditoria() utiliza REQUIRES_NEW, su transacción puede confirmarse aunque después falle procesarPedido() y se revierta la transacción exterior.
3. Detalles importantes en Spring
    • Proxy de Spring: normalmente, @Transactional se aplica mediante un proxy. Una llamada a otro método de la misma instancia (this.otroMetodo()) puede evitar ese proxy y, por tanto, no activar la configuración transaccional esperada.
    • Límite transaccional: suele ser preferible definirlo en métodos de servicio que representan una operación de negocio.
    • Transacciones y HTTP: una transacción de base de datos no hace que una llamada HTTP externa forme parte automáticamente de la misma transacción.
    • Duración: conviene mantener las transacciones razonablemente cortas para reducir bloqueos y contención.
Pregunta de comprobación
Un método de servicio tiene @Transactional con el comportamiento predeterminado REQUIRED. Llama a otro método que también utiliza REQUIRED. Si ya hay una transacción activa, ¿qué ocurre normalmente?
A. El segundo método siempre crea una transacción independiente.
B. El segundo método se une a la transacción existente.
C. Spring desactiva la transacción exterior.
D. REQUIRED impide que el segundo método acceda a la base de datos.
Comprobar
Correcto.
La respuesta es B. REQUIRED reutiliza la transacción activa; si no existe ninguna, inicia una. Por eso, normalmente, ambas operaciones comparten el mismo contexto transaccional.
Continuar con Spring Boot

Fase 3 — Spring Boot
Bloque 34: Spring Security
Spring Security es el framework de Spring que permite proteger aplicaciones mediante autenticación, autorización y otras defensas de seguridad.
La diferencia fundamental es:
    • Autenticación: comprobar quién eres.
    • Autorización: comprobar qué tienes permitido hacer.
Por ejemplo, iniciar sesión autentica a un usuario; permitir que solo los administradores eliminen usuarios es autorización.
1. Configurar la seguridad
En Spring Boot moderno, la configuración habitual utiliza un bean SecurityFilterChain.
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http)
            throws Exception {

        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/publico/**").permitAll()
                .requestMatchers("/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .httpBasic(Customizer.withDefaults())
            .build();
    }
}
En este ejemplo:
    • /publico/** es accesible sin iniciar sesión.
    • /admin/** requiere el rol ADMIN.
    • El resto de rutas requiere autenticación.
    • httpBasic() habilita autenticación HTTP Basic, adecuada para ejemplos o ciertos escenarios, pero en producción debe utilizarse sobre HTTPS y elegirse el mecanismo de autenticación según las necesidades.
Esta configuración controla el acceso a las peticiones HTTP. La aplicación también necesita una forma de obtener y verificar las identidades de los usuarios.
2. Roles y permisos
Spring Security permite restringir el acceso según roles o autoridades.
.requestMatchers("/admin/**").hasRole("ADMIN")
.requestMatchers("/informes/**").hasAuthority("REPORT_READ")
La diferencia habitual:
    • hasRole("ADMIN") busca la autoridad ROLE_ADMIN.
    • hasAuthority("REPORT_READ") busca exactamente REPORT_READ.
Los roles suelen representar categorías de usuario; las autoridades pueden expresar permisos más específicos.
3. Contraseñas seguras
Nunca debes almacenar contraseñas en texto plano. Spring Security proporciona PasswordEncoder para almacenarlas mediante algoritmos de hash diseñados para contraseñas, como BCrypt.
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder();
}
Para guardar una contraseña:
String hash = passwordEncoder.encode(password);
Para verificarla posteriormente:
boolean correcta = passwordEncoder.matches(password, hash);
No se compara el hash generado en una nueva ejecución con el anterior directamente: BCrypt utiliza sal y puede producir hashes diferentes para la misma contraseña. matches() realiza la comprobación correctamente.
4. Sesiones, JWT y CSRF
Son conceptos relacionados, pero diferentes:
    • Sesión: el servidor mantiene el estado de autenticación asociado a una sesión, normalmente identificada por una cookie.
    • JWT: token que contiene declaraciones firmadas y que puede permitir validar la identidad sin consultar una sesión tradicional en cada petición. No está cifrado necesariamente.
    • CSRF: ataque que intenta inducir al navegador de un usuario autenticado a realizar acciones no deseadas. La protección es especialmente importante cuando las credenciales se envían automáticamente, como ocurre con cookies de sesión.
No debes desactivar CSRF por costumbre. En una API que autentica mediante tokens enviados explícitamente en una cabecera y no utiliza credenciales enviadas automáticamente por el navegador, la configuración puede ser distinta. La decisión depende del mecanismo de autenticación y del cliente.
Pregunta de comprobación
Una aplicación permite iniciar sesión correctamente, pero quiere garantizar que solo los usuarios con rol de administrador puedan acceder a /admin/**. ¿Qué mecanismo debe aplicar?
A. Autenticación: comprobar de nuevo la contraseña en cada endpoint.
B. Autorización: restringir la ruta mediante hasRole("ADMIN").
C. Cifrar el nombre de usuario con BCrypt.
D. Activar @Transactional en el controlador.
Comprobar
Correcto.
La respuesta es B. La autenticación identifica al usuario; la autorización determina si tiene permiso para acceder a un recurso. hasRole("ADMIN") restringe el acceso a usuarios que tengan la autoridad ROLE_ADMIN.
Continuar con Spring Boot



Fase 3 — Spring Boot
Bloque 35: Configuración externa y variables de entorno
En una aplicación Spring Boot, la configuración debe estar separada del código para poder ejecutar la misma aplicación en desarrollo, pruebas y producción sin modificar las clases Java.
Por ejemplo, la URL de la base de datos, las credenciales y el puerto pueden variar según el entorno.
1. application.properties y application.yml
Spring Boot permite configurar la aplicación mediante src/main/resources/application.properties:
server.port=8081

spring.datasource.url=${DB_URL}
spring.datasource.username=${DB_USER}
spring.datasource.password=${DB_PASSWORD}
También puedes usar YAML (application.yml):
server:
  port: 8081

spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USER}
    password: ${DB_PASSWORD}
Ambos formatos permiten definir propiedades de configuración. No necesitas utilizar los dos a la vez.
La sintaxis ${DB_URL} indica que Spring debe obtener el valor de la propiedad DB_URL desde una fuente de configuración disponible, normalmente una variable de entorno en este ejemplo.
2. Perfiles: desarrollo, pruebas y producción
Los perfiles permiten activar configuraciones diferentes según el entorno.
Por ejemplo, application-dev.properties:
server.port=8081
spring.datasource.url=jdbc:postgresql://localhost:5432/app_dev
Y application-prod.properties:
server.port=8080
spring.datasource.url=${DB_URL}
Puedes activar un perfil con la variable de entorno:
SPRING_PROFILES_ACTIVE=prod
O mediante una propiedad de configuración equivalente.
Importante: no guardes contraseñas reales ni claves privadas en los archivos versionados de Git. En producción, utiliza variables de entorno o un gestor de secretos apropiado.
3. Leer configuración desde Java
Para una propiedad concreta puedes usar @Value:
@Component
public class ApiConfig {

    @Value("${api.timeout:5000}")
    private int timeout;
}
Aquí, 5000 es el valor predeterminado si no se define api.timeout.
Para un conjunto de propiedades relacionadas, suele ser más mantenible utilizar @ConfigurationProperties:
@ConfigurationProperties(prefix = "api")
public record ApiProperties(
    int timeout,
    String baseUrl
) {}
Y registrar esas propiedades, por ejemplo, con @ConfigurationPropertiesScan en la aplicación.
Si la configuración es:
api.timeout=5000
api.base-url=https://api.example.com
Spring vincula esos valores con los campos correspondientes. Esta opción facilita agrupar, tipar y validar la configuración.
4. ¿Cómo se resuelven los valores?
Spring Boot utiliza distintas fuentes de configuración, como archivos de propiedades, variables de entorno y argumentos de línea de comandos. Cuando varias fuentes definen la misma propiedad, se aplican reglas de precedencia.
Esto permite, por ejemplo, mantener una configuración predeterminada en el proyecto y sobrescribir la URL de la base de datos en producción sin cambiar el código.
Pregunta de comprobación
Tienes una aplicación Spring Boot que se ejecuta en desarrollo y producción. Cada entorno utiliza una base de datos diferente. ¿Cuál es la solución más adecuada?
A. Escribir la URL de producción directamente en cada clase Java que accede a la base de datos.
B. Mantener la configuración externa, usando perfiles y propiedades como ${DB_URL} para adaptar el entorno.
C. Crear una versión diferente del código Java para cada base de datos.
D. Guardar las contraseñas de producción en el repositorio Git para que todos los entornos puedan leerlas.
Comprobar
Correcto.
La respuesta es B. La configuración externa y los perfiles permiten adaptar la aplicación al entorno sin modificar el código. Las credenciales deben mantenerse fuera del repositorio y gestionarse de forma segura.

