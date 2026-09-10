# BatchProcessor

Motor de integración de datos sobre Spring Batch. Mueve registros entre **CSV**,
**API REST** y **base de datos** en cualquier combinación, y la entidad que
procesa no se decide al compilar: se resuelve en tiempo de ejecución.

Java 17 · Spring Boot 3.3.4 · Spring Batch · JPA/Hibernate · MySQL

---

## Cómo funciona

No hay ningún `Job` declarado en el código. El endpoint `/batch/run` recibe los
**nombres de tres beans** —lector, procesador y escritor—, los saca del contexto
de Spring, compone un `Step` y un `Job` en ese momento, y los lanza.

```
POST /batch/run?reader=csvItemReader&processor=genericProcessor&writer=databaseItemWriter
```

La entidad **no viaja en la petición**: sale de la propiedad `entityClass` y se
pasa como parámetro del job. Cada componente la resuelve con `Class.forName`
cuando arranca el paso.

```
  application.properties                      petición HTTP
    entityClass ────┐                   reader / processor / writer
    csv.file.path   │                  (+ transactionManager opcional)
    apiToReadUrl    │                              │
                    ▼                              ▼
              BatchController compone Step + Job y lo lanza
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
          lector              procesador              escritor
      (CSV/API/BD)      (mapea si hace falta)      (CSV/API/BD)
```

Componer el job en caliente es lo que permite las nueve combinaciones sin
escribir una clase por cada una. El precio es que los errores de configuración
no aparecen al arrancar sino al lanzar el job.

### Un cuarto parámetro: `transactionManager`

Opcional. Si no se envía, el paso se ejecuta con el gestor de transacciones de
la base de datos principal, que es lo que necesitan ocho de las nueve rutas.

Hace falta nombrarlo en un solo caso: **escribir en la segunda base de datos**.
`JpaItemWriter` persiste con el `EntityManager` asociado al gestor que gobierna
el paso, así que escritor y gestor tienen que apuntar a la misma base. Si no
coinciden, la escritura falla con «No EntityManager with actual transaction
available».

```
POST /batch/run?reader=databaseItemReader&processor=genericProcessor
                &writer=secondDatabaseItemWriter
                &transactionManager=secondTransactionManager
```

Se pide por nombre, igual que los otros tres, en vez de deducirlo del escritor:
una regla implícita dentro del controlador sería una cosa más que recordar cada
vez que se añada un escritor.

---

## Rutas soportadas

Tres orígenes por tres destinos. **Las nueve tienen un test que las ejecuta de
punta a punta**, comprobando el resultado —filas en la tabla, líneas en el
fichero, peticiones enviadas— y no solo que el job termine en `COMPLETED`.

| Origen → Destino | Test |
|---|---|
| CSV → base de datos | ✅ `JobCsvADatabaseTest` · `JobCsvAPersonaEnBaseDeDatosTest` |
| CSV → CSV | ✅ `JobCsvACsvTest` |
| CSV → API | ✅ `JobCsvAApiTest` |
| Base de datos → CSV | ✅ `JobDatabaseACsvTest` |
| Base de datos → API | ✅ `JobDatabaseAApiTest` |
| Base de datos → base de datos | ✅ `JobDatabaseADatabaseTest` |
| API → API | ✅ `JobApiAApiTest` |
| API → CSV | ✅ `JobApiACsvTest` |
| API → base de datos | ✅ `JobApiADatabaseTest` |

Las dos últimas llevaron un tiempo marcadas como cubiertas sin estarlo: había un
test del lector de API y otros de los escritores, y de ahí se dedujo que la
combinación funcionaba. Deducir no es probar, así que ahora tienen su propio
recorrido. Los dos usan `Persona` en lugar de `GenericEntity` —tres campos, y
una entidad que no hereda de nada— y comprueban un campo concreto además del
recuento: un lector que devolviera mapas podría dejar el número de filas bien y
los campos vacíos.

### Las nueve peticiones, literales

Siempre son las mismas tres piezas: un lector, `genericProcessor` y un escritor.
Basta con copiar la línea que corresponda y cambiarle el host.

```bash
# ── Desde CSV (necesita csv.file.path) ──────────────────────────────────────
curl -X POST "localhost:8080/batch/run?reader=csvItemReader&processor=genericProcessor&writer=databaseItemWriter"
curl -X POST "localhost:8080/batch/run?reader=csvItemReader&processor=genericProcessor&writer=csvItemWriter"
curl -X POST "localhost:8080/batch/run?reader=csvItemReader&processor=genericProcessor&writer=apiItemWriter"

# ── Desde base de datos ─────────────────────────────────────────────────────
curl -X POST "localhost:8080/batch/run?reader=databaseItemReader&processor=genericProcessor&writer=csvItemWriter"
curl -X POST "localhost:8080/batch/run?reader=databaseItemReader&processor=genericProcessor&writer=apiItemWriter"
curl -X POST "localhost:8080/batch/run?reader=databaseItemReader&processor=genericProcessor&writer=secondDatabaseItemWriter&transactionManager=secondTransactionManager"

# ── Desde API (necesita apiToReadUrl) ───────────────────────────────────────
curl -X POST "localhost:8080/batch/run?reader=apiItemReader&processor=genericProcessor&writer=csvItemWriter"
curl -X POST "localhost:8080/batch/run?reader=apiItemReader&processor=genericProcessor&writer=databaseItemWriter"
curl -X POST "localhost:8080/batch/run?reader=apiItemReader&processor=genericProcessor&writer=apiItemWriter"
```

La sexta es la única con cuatro parámetros. Las demás usan el gestor de
transacciones por defecto.

Qué propiedad tiene que estar puesta según los extremos que uses:

| Si el origen es | Hace falta | Si el destino es | Hace falta |
|---|---|---|---|
| CSV | `csv.file.path` | CSV | `csv.output.file.path` |
| base de datos | nada más | base de datos | nada más |
| API | `apiToReadUrl` | API | `apiToWriteUrl` |
| | | segunda base de datos | `second.datasource.*` |

Y en todos los casos, `entityClass`.

**Tres de esas rutas estaban rotas** cuando se escribieron los tests, y las tres
fallaban sin decirlo: dos por una colisión de nombres de bean y una por un
escritor que multiplicaba los envíos. Están descritas más abajo, en las notas y
en las limitaciones.

### Cuándo hace falta un procesador propio en las rutas de API

La respuesta corta: **cuando la API devuelva una forma distinta de tu entidad**
—campos con otro nombre, estructuras anidadas, valores que haya que
transformar—. Si la devuelve con la misma forma, `genericProcessor` basta.

Lo que importa es que la frontera se ha movido, y conviene saber de dónde a
dónde para no reintroducir lo viejo.

**Antes hacía falta uno por cada entidad, siempre, aunque el JSON encajara
perfectamente.** `ApiItemReader` pedía la respuesta con
`ParameterizedTypeReference<List<T>>`; ese `T` es una variable de tipo que Java
borra al compilar, así que en ejecución no había clase concreta que darle a
Jackson y la respuesta llegaba como lista de `LinkedHashMap`. El procesador
rehacía la entidad campo a campo — que no era mapeo de negocio, era compensar el
borrado de tipos. Añadir una entidad significaba escribir su procesador, sin
excepción.

**Ahora hace falta uno por cada API que no encaje**, y solo entonces. El lector
construye el tipo con la clase que ya resuelve `Class.forName`, así que Jackson
deserializa directamente en la entidad.

De obligatorio y mecánico, a opcional y con motivo. Un procesador que solo copie
campos de un mapa a un objeto es señal de que alguien está reintroduciendo el
problema viejo; uno que renombre, aplane o convierta es mapeo de verdad y es
legítimo.

---

## Beans disponibles

Casi todos se registran por **escaneo de componentes**: las clases llevan
`@Component` y el bean toma el nombre de la clase con la inicial en minúscula.

| Bean | Cómo se registra | Qué hace |
|---|---|---|
| `csvItemReader` | `@Component` | Lee `csv.file.path`. Valida cabeceras contra la entidad |
| `csvItemWriter` | `@Component` | Escribe en `csv.output.file.path` |
| `apiItemReader` | `@Component` | Hace GET a `apiToReadUrl` |
| `apiItemWriter` | `@Component` | Hace POST a `apiToWriteUrl` |
| `genericProcessor` | `@Component` | Pasa los elementos sin tocarlos |
| `databaseItemReader` | `@Bean` en `BatchConfig` | Lee con JPA. Necesita el parámetro del job |
| `databaseItemWriter` | `@Bean` en `BatchConfig` | `JpaItemWriter`: persiste **cualquier** `@Entity` |
| `secondDatabaseItemWriter` | `@Bean` en `BatchConfig` | Igual, contra la **segunda** base de datos |

Y los gestores de transacciones, que solo se nombran en la petición cuando se
usa la segunda base de datos:

| Bean | Base de datos |
|---|---|
| `transactionManager` | Principal. Es el primario: se usa si no se dice otra cosa |
| `secondTransactionManager` | Segunda. Hay que pedirlo explícitamente |

> **Una colisión de nombres que rompió la lectura desde base de datos, y cómo
> apareció.** Estas rutas funcionaban cuando el proyecto se escribió. La clase
> se llamaba entonces `DatabaseReader`, así que el bean que generaba el escaneo
> era `databaseReader` y convivía sin problema con el `@Bean` explícito
> `databaseItemReader`.
>
> Al renombrarla a `DatabaseItemReader`, el bean escaneado pasó a llamarse igual
> que el explícito. En esa colisión **gana el escaneado**, que es una fábrica y
> no implementa `ItemReader`, así que el controlador empezó a reventar con un
> `ClassCastException` al componer el paso. Nadie se enteró porque
> `spring.main.allow-bean-definition-overriding=true` evitaba que Spring
> protestara al arrancar.
>
> Se retiraron `@Component` y `@StepScope` de la clase —el `@StepScope` pasó al
> `@Bean`, que es donde hace falta para leer `jobParameters`—, de modo que solo
> hay un bean con ese nombre.
>
> Lo destapó `JobDatabaseACsvTest`, el primer test que ejecutó esa ruta: un
> renombrado aparentemente inocuo rompió dos rutas durante meses sin un solo
> mensaje de error.
>
> **La propiedad que lo tapaba sigue puesta, y no por olvido.** Se intentó
> quitar y la aplicación dejó de arrancar por otra colisión distinta:
> `BatchAutoConfiguration` de Spring Boot registra `jobRepository` y
> `jobLauncher` sin comprobar si ya existen, y `BatchConfig` declara los dos a
> propósito. Ver la nota en `application.properties`.

---

## Propiedades de configuración

En `src/main/resources/application.properties`:

| Propiedad | Para qué |
|---|---|
| `entityClass` | Nombre completo de la entidad. Se pasa como parámetro del job |
| `csv.file.path` | CSV de entrada, relativo al classpath |
| `csv.output.file.path` | Ruta del CSV de salida |
| `apiToReadUrl` | Endpoint del que leer |
| `apiToWriteUrl` | Endpoint al que escribir |
| `second.datasource.*` | `url`, `username`, `password` y `driver-class-name` de la segunda base de datos |

Solo hacen falta las que use la ruta que vayas a ejecutar. Las de la segunda
base de datos apuntan por defecto a otro esquema del mismo MySQL (`generic2`),
que se crea solo con `createDatabaseIfNotExist=true`.

---

## Cambiar la entidad que se procesa

Es lo que hace genérico al motor y donde están todas las trampas. El proyecto
trae dos entidades:

| Entidad | Campos |
|---|---|
| `GenericEntity` | `id`, `data` |
| `Persona` | `personaId`, `nombreCompleto`, `empleo` |

Las dos sirven para **todas** las rutas. Hasta hace poco `Persona` no podía
escribirse en base de datos, porque el escritor exigía heredar de
`GenericEntity`; eso se ha resuelto y hay un test que lo comprueba.

### Caso simple: usar una de las dos

1. Prepara el CSV con las cabeceras **exactas** de la entidad: `id,data` para
   `GenericEntity`, o `personaId,nombreCompleto,empleo` para `Persona`.
2. Apunta `csv.file.path` a ese fichero.
3. Ajusta `entityClass` al nombre completo de la clase.
4. Lanza el job con los beans de la ruta que quieras.

El `input.csv` que viene en `src/main/resources` es genérico —cabeceras
`id,data`—, y `entityClass` apunta por defecto a `GenericEntity`, así que el
ejemplo funciona sin tocar nada.

### Caso real: añadir una entidad propia

El objetivo de estos cinco pasos es que una clase nueva funcione en **las nueve
direcciones**, no solo en la que vayas a usar hoy.

**Paso 1 — Crea la clase** en `com.example.BatchProcessor.model`, anotada
`@Entity` con su `@Table`, con **constructor sin argumentos** y getters y
setters de todos los campos.

```java
@Entity
@Table(name = "producto")
public class Producto {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nombre;
    private Double precio;

    public Producto() {}   // obligatorio: lo usan Jackson y Hibernate

    // getters y setters de los tres campos
}
```

Tres detalles que no son adorno:

- **No tiene que heredar de nada.** `databaseItemWriter` persiste vía
  `EntityManager` y acepta cualquier `@Entity`. La versión anterior exigía
  heredar de `GenericEntity` y por eso `Persona` no podía guardarse.
- **El constructor vacío es obligatorio.** Sin él, Jackson no puede
  deserializar la respuesta de la API y Hibernate no puede instanciar la entidad.
  Es el fallo más frecuente al añadir una clase.
- **Los getters mandan en lo que sale.** El escritor de CSV y el de API
  serializan por propiedades, así que un campo sin getter viaja vacío o no
  viaja.

> **Consejo, con cicatriz.** Nombra los campos en minúsculas o con guion bajo
> (`nombre`, `fecha_alta`), no en camelCase (`nombreCompleto`). El motor funciona
> igual con ambos, pero el nombre del campo acaba siendo el nombre de la columna,
> y las columnas con mayúsculas en medio dan guerra en cuanto escribes SQL a
> mano: los motores pasan a mayúsculas los identificadores que no van entre
> comillas, así que `WHERE nombreCompleto = ...` busca `NOMBRECOMPLETO` y falla
> con «bad SQL grammar»; entrecomillar tampoco arregla nada, porque entonces hay
> que acertar la capitalización exacta con la que Hibernate creó la columna.
> `Persona` está así y por eso `JobApiADatabaseTest` no nombra ni una columna en
> su consulta. Si heredas una entidad en camelCase, usa `@Column(name = "...")`
> para darle a la columna un nombre en minúsculas.

**La tabla no hay que crearla a mano.** Con `ddl-auto=create` Hibernate la genera
al arrancar a partir de la clase. Eso también significa que **se borra y se
recrea en cada arranque**, así que no dejes ahí nada que te importe.

**Paso 2 — Cuadra las cabeceras del CSV**, si vas a leer de fichero. La
validación es literalmente esta:

```java
Set<String> fieldNames = Arrays.stream(entityType.getDeclaredFields())
        .map(Field::getName)
        .collect(Collectors.toSet());
```

Tres consecuencias:

- Se comparan **nombres de campos Java**, no de `@Column`. Si el campo es
  `nombreCompleto` y la columna `nombre_completo`, la cabecera dice
  `nombreCompleto`.
- Distingue mayúsculas.
- `getDeclaredFields()` devuelve solo los campos **declarados por la clase**, no
  los heredados. Si tu entidad hereda de otra, los campos del padre no valen
  como cabeceras. Antes esto era una trampa seria, porque escribir en base de
  datos obligaba a heredar de `GenericEntity`; ya no, así que en la práctica
  solo aparece si decides construir una jerarquía por tu cuenta.

Para `Producto`, el fichero empieza así:

```csv
id,nombre,precio
1,Teclado,49.90
2,Monitor,189.00
```

**Paso 3 — Cuadra el JSON**, si vas a leer de una API. Los nombres de las
propiedades del JSON tienen que coincidir con los de la entidad; el lector
deserializa directamente en la clase.

```json
[
  {"id": 1, "nombre": "Teclado", "precio": 49.90},
  {"id": 2, "nombre": "Monitor", "precio": 189.00}
]
```

Si la API que tienes delante devuelve otra cosa —campos con otro nombre,
estructuras anidadas—, anota los campos con `@JsonProperty` o escribe un
procesador propio. Ese es mapeo de verdad, y es el único caso en que
`genericProcessor` no basta.

**Paso 4 — Ajusta la configuración.**

```properties
entityClass=com.example.BatchProcessor.model.Producto
csv.file.path=productos.csv
csv.output.file.path=salida-productos.csv
apiToReadUrl=http://localhost:8081/productos
apiToWriteUrl=http://localhost:8081/productos
```

Solo hacen falta las de los extremos que vayas a usar; la tabla está en «Las
nueve peticiones».

**Paso 5 — Compruébalo sin arrancar nada.** Copia un caso de `CsvItemReaderTest`
con tu entidad y tu CSV: valida las cabeceras en milisegundos, sin servidor ni
base de datos. Es más rápido que levantarlo todo y descubrirlo por un 500.

Y si vas a mover la entidad en serio, copia además el test de la ruta que te
importe —están todos en `src/test/java`, uno por dirección— cambiando
`entityClass`. Cada uno es unas cuarenta líneas y te dice si la clase funciona
de punta a punta antes de conectarla a nada real.

### Recorrido completo, de principio a fin

`Producto` ya creado y `entityClass` apuntando a él. Tres direcciones seguidas,
sin tocar una línea de Java entre una y otra:

```bash
# 0. Arranca. Hibernate crea la tabla producto a partir de la clase.
mvn spring-boot:run

# 1. Del CSV a la base de datos.
#    Requiere csv.file.path=productos.csv con cabeceras id,nombre,precio
curl -X POST "localhost:8080/batch/run?reader=csvItemReader&processor=genericProcessor&writer=databaseItemWriter"

# 2. De la base de datos a un CSV nuevo. Ida y vuelta: comprueba el redondeo,
#    los acentos y los nulos mejor que mirar la tabla.
#    Requiere csv.output.file.path
curl -X POST "localhost:8080/batch/run?reader=databaseItemReader&processor=genericProcessor&writer=csvItemWriter"

# 3. De la base de datos a la API.
#    Requiere apiToWriteUrl, y algo escuchando ahí
curl -X POST "localhost:8080/batch/run?reader=databaseItemReader&processor=genericProcessor&writer=apiItemWriter"
```

Cada llamada responde `Job started successfully!` o un 500 genérico. **El
detalle del error nunca va en la respuesta**, va al log del servidor: si algo
falla, la consola donde arrancaste es el sitio donde mirar, no la terminal donde
lanzaste el `curl`.

Un aviso sobre el paso 2: `csvItemWriter` **añade al final del fichero** en vez
de sobrescribir. Si repites la llamada sin borrar la salida, las filas se
acumulan y parece que el job las ha duplicado. No las ha duplicado.

### Qué le pide cada dirección a tu clase

| Dirección | Lo que exige de la entidad |
|---|---|
| Leer de CSV | Cabeceras = campos **declarados**, con mayúsculas exactas |
| Escribir en CSV | Getters; las columnas salen en orden de declaración |
| Leer de API | Constructor vacío; nombres del JSON = nombres de los campos |
| Escribir en API | Getters (se serializa el objeto entero) |
| Leer de base de datos | `@Entity` mapeada; nada más |
| Escribir en base de datos | `@Entity` con `@Id`; **no** hace falta heredar de nada |

Dicho de otro modo: si la clase tiene `@Entity`, `@Id`, constructor vacío y
getters/setters de todo, **ya sirve para las nueve**. Lo demás son requisitos de
los datos —cabeceras del CSV, nombres del JSON—, no de la clase.

**No hace falta escribir un procesador** para ninguna de las nueve.
`genericProcessor` vale para todas, incluidas las de API. La única excepción es
la del paso 3: que la API devuelva una forma distinta de tu entidad.

### Errores y qué significan

| Mensaje | Causa |
|---|---|
| `The job parameter 'entityClass' is required` | Falta la propiedad `entityClass` |
| `Class not found: X` | Nombre de clase mal escrito, o la clase no existe |
| `Unknown header in CSV file: X` | `X` no es un campo **declarado** por la entidad |
| `The CSV file does not contain headers` | El fichero está vacío |
| `No bean named 'X' available` | El nombre del bean en la petición está mal |
| `No EntityManager with actual transaction available` | Escritor y `transactionManager` apuntan a bases distintas |
| `Cannot construct instance of X (no Creators...)` | A la entidad le falta el constructor sin argumentos |
| `Unknown property 'X'` al leer de la API | El JSON trae un campo que la entidad no declara |
| Filas en la tabla pero campos vacíos | Faltan getters/setters, o los nombres del JSON no coinciden |

El endpoint responde **500 con un mensaje genérico** a propósito:
`e.getMessage()` puede exponer rutas y consultas SQL a quien llame a la API. El
detalle está en el log del servidor.

---

## Ejecución

### Requisitos

- JDK 17 o superior
- Maven
- MySQL en `localhost:3306` — las bases se crean solas
  (`createDatabaseIfNotExist=true`)

### Arrancar

```bash
mvn spring-boot:run
```

El esquema se recrea en cada arranque (`ddl-auto=create`), así que **se pierden
los datos anteriores**. Vale para desarrollo y para nada más.

La aplicación escucha en el **8080**. Swagger en `/swagger-ui/index.html`,
servido por **springdoc**.

Las rutas de API apuntan por defecto al **8081**, es decir, a un segundo
servicio que debes tener levantado si vas a usarlas.

### Tests

```bash
mvn test
```

Dieciocho tests que **no necesitan MySQL ni red**: corren sobre H2 en memoria
mediante el perfil `test`, y la API se simula con `MockRestServiceServer`.
Cubren el arranque del contexto, la resolución de la entidad por reflexión, la
validación de cabeceras del CSV, la deserialización de la respuesta de la API en
entidades, el reinicio del estado del lector entre pasos y **las nueve rutas de
punta a punta**.

Dos detalles que hacen que valgan algo:

- El recorrido CSV → base de datos ejecuta la **configuración real** del
  proyecto, no una inventada para el test: si `entityClass` dejara de encajar
  con `input.csv`, lo detectaría.
- El de base de datos → base de datos usa **dos bases H2 distintas**
  (`batchprocessor` y `batchprocessor_destino`). Si fueran la misma, el job
  leería y escribiría en el mismo sitio y el test pasaría sin demostrar nada.
  Comprueba además que las filas **siguen** en el origen: un job que moviera en
  vez de copiar también las dejaría en el destino.

---

## Limitaciones conocidas

- **La ruta base de datos → base de datos solo está probada contra H2.** El
  `JobRepository` se construye con `setDatabaseType("MYSQL")` fijo, y las dos
  bases del test son H2 en memoria. Que funcione ahí no garantiza que funcione
  contra dos esquemas MySQL reales: eso hay que probarlo a mano antes de fiarse.
- **Credenciales versionadas.** `application.properties` lleva `root` / `1234`
  para las dos bases. Son de desarrollo local, pero están en el repositorio.
- **Cambiar de entidad exige reiniciar**: `entityClass` se lee al construir el
  controlador.
- **`ApiItemWriter` multiplicaba los envíos.** Iteraba sobre cada elemento del
  bloque y en cada vuelta enviaba la lista completa: diez registros generaban
  diez peticiones de diez registros, cien en total, y el job terminaba en
  COMPLETED porque todas respondían 200. Corregido, con test que cuenta las
  peticiones. Afectaba a las tres rutas que escriben en una API.
- **Código sin efecto en `CsvItemWriter`.** Hay unas veinte líneas que
  construyen un `CsvSchema` con las columnas invertidas —`getColumnNames()`,
  `Collections.reverse`, un `CsvSchema.Builder` nuevo— y ese esquema se pasa al
  escritor. Un test comprobó que la salida sale en el orden de declaración de la
  entidad, así que el bloque no hace nada. El motivo está sin averiguar; el
  comportamiento sí está fijado por `JobCsvACsvTest`.
- **`CsvItemWriter` añade al final del fichero** en vez de sobrescribir, y la
  comprobación de si hay que escribir cabecera se hace *después* de abrir el
  `FileWriter`, que ya ha creado el fichero. Funciona porque queda en pie
  `file.length() == 0`, pero no por lo que el código aparenta comprobar.
- **`spring.main.allow-bean-definition-overriding=true` sigue activada.** Ya no
  tapa la colisión de `databaseItemReader` —esa está resuelta—, pero sí una
  segunda: `BatchAutoConfiguration` registra `jobRepository` y `jobLauncher` sin
  condición de «solo si no existen», y `BatchConfig` los declara a propósito.

  > **Pendiente — la salida buena, sin hacer.** Existe, y es más interesante que
  > quitar la propiedad: **dejar de declarar `jobRepository` y `jobLauncher` en
  > `BatchConfig` y quedarse con los de la autoconfiguración.** Eso mataría dos
  > pájaros — desaparece la colisión *y* desaparece el `setDatabaseType("MYSQL")`
  > fijo, que es exactamente el caveat de la limitación anterior sobre por qué el
  > test de base de datos a base de datos no garantiza nada contra MySQL real.
  > Boot deduce el tipo de la conexión.
  >
  > No está hecho porque hay que averiguar —probando, no suponiendo— qué gestor
  > de transacciones acaba usando el `JobRepository` de Boot y si
  > `spring.batch.jdbc.initialize-schema` se sigue aplicando. Ambas cosas las
  > dice un `mvn test`, no el razonamiento.
- **Código muerto que sigue en el repositorio.** `BatchScheduler` es una clase
  `@Component` cuyo cuerpo entero está comentado, y `BatchJobProperties` lee un
  `batch.job.cron` que ya no existe en la configuración: sobran las dos si no se
  va a recuperar la ejecución programada. `DatabaseItemWriter.ManualItemWriter`
  ya no lo usa ningún bean; se conserva a propósito, porque escribir con un
  repositorio de Spring Data sigue siendo útil si algún día hace falta lógica
  propia en el guardado.

### Resuelto

- ~~Ocho de las nueve rutas sin test de recorrido completo.~~ Las nueve lo
  tienen.
- ~~Base de datos → base de datos sin implementar.~~ Implementada con un segundo
  `DataSource`, `EntityManagerFactory` y `TransactionManager` en
  `SecondDatabaseConfig`.
- ~~`springfox-swagger2` y `springfox-swagger-ui` en el `pom.xml`.~~ Retiradas.
  No se importaban en ninguna clase —la documentación la sirve springdoc— y
  además no podían funcionar: springfox 3.0.0 está compilado contra
  `javax.servlet` y Spring Boot 3 usa `jakarta.servlet`.
