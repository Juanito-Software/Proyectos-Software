Fase 3.5 — Spring Batch
Bloque 36: Jobs, Steps y JobParameters
Spring Batch es un framework de Spring diseñado para procesar grandes volúmenes de datos mediante trabajos por lotes (batch processing).

Por ejemplo, puedes leer un CSV, transformar sus registros y guardarlos en PostgreSQL, o sincronizar información entre una API y una base de datos.

Los tres conceptos fundamentales son Job, Step y JobParameters.
1. Job: el trabajo completo
Un Job representa el proceso por lotes completo.

Por ejemplo, un trabajo que importa usuarios desde un CSV a una base de datos.
2. Step: una etapa del trabajo
Un Job está compuesto por uno o varios Step. Cada etapa representa una parte del proceso.
Job: importar usuarios

Step 1: leer y validar CSV

Step 2: guardar en PostgreSQL


En un trabajo sencillo puedes tener un solo Step. En procesos más complejos, puedes separar lectura, validación, transformación y otras operaciones.
3. JobParameters: parámetros de ejecución
Los JobParameters permiten pasar datos al trabajo cuando se inicia.

Por ejemplo:
- La ruta del archivo que se va a procesar.
- La fecha de importación.
- El identificador de un cliente.
- Un parámetro que identifica una ejecución lógica concreta.
Así evitas codificar valores fijos dentro del trabajo.

En Spring Batch, los parámetros también intervienen en la identificación de las instancias del Job. Por defecto, los parámetros identificadores determinan si se trata de una instancia existente o de una nueva.
4. Ejemplo con Spring Batch
Este es un ejemplo simplificado de configuración con la API de Spring Batch 5:

---

@Configuration
public class ImportJobConfig {

    @Bean
    public Job importJob(
            JobRepository jobRepository,
            Step importStep) {

        return new JobBuilder("importJob", jobRepository)
                .start(importStep)
                .build();
    }

    @Bean
    public Step importStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager) {

        return new StepBuilder("importStep", jobRepository)
                .tasklet((contribution, chunkContext) -> {
                    System.out.println("Procesando importación...");
                    return RepeatStatus.FINISHED;
                }, transactionManager)
                .build();
    }
}

---

En este ejemplo:
- JobBuilder construye el trabajo.
- StepBuilder construye una etapa.
- JobRepository gestiona los metadatos de Spring Batch.
- PlatformTransactionManager gestiona la transacción del Step.
- tasklet ejecuta una operación sencilla y termina cuando devuelve RepeatStatus.FINISHED.
Este ejemplo utiliza un Tasklet, adecuado para una operación sencilla. En los siguientes bloques veremos el procesamiento por chunks, más apropiado para leer, transformar y escribir conjuntos de registros.

Relación con BatchProcessor: cuando tu motor ejecuta diferentes rutas de integración —por ejemplo, CSV → API o base de datos → base de datos—, el Job representa el proceso completo y los Step organizan las operaciones que lo componen.

Pregunta de comprobación
Quieres ejecutar un trabajo de importación indicando en cada ejecución qué archivo CSV debe procesar. ¿Qué mecanismo de Spring Batch está pensado para pasar esa información al iniciar el trabajo?

A. JobParameters.


B. @Entity.


C. PlatformTransactionManager.


D. @RestController.


ComprobarCorrecto.

La respuesta es A: JobParameters. Permiten pasar valores como la ruta del CSV y forman parte de la identificación de las instancias del trabajo, según cuáles sean identificadores.

---

Fase 3.5 — Spring Batch
Bloque 37: Procesamiento por chunks
El procesamiento por chunks permite procesar datos en grupos de registros, en lugar de cargar todo el conjunto en memoria o gestionar cada registro mediante una transacción independiente.

Es especialmente útil para importar CSV, sincronizar APIs y escribir grandes cantidades de registros en una base de datos.
1. ¿Cómo funciona un chunk?
Un Step basado en chunks utiliza tres componentes principales:
1. ItemReader: lee un registro de entrada.
2. ItemProcessor: transforma o valida el registro.
3. ItemWriter: escribe los registros procesados.
Spring Batch repite el ciclo hasta reunir el tamaño de chunk configurado, o llegar al final de los datos.
ItemReader

Lee registros de entrada

ItemProcessor

Valida y transforma cada registro

ItemWriter

Escribe el grupo de registros

Commit de la transacción

Después, continúa con el siguiente chunk


Por ejemplo, con un chunk de tamaño 100, Spring Batch procesa hasta 100 elementos antes de escribir el grupo y confirmar la transacción correspondiente.

Si quedan 35 registros al final, el último chunk puede contener solo esos 35.
2. Configurar un chunk en Java
Ejemplo simplificado con Spring Batch 5:

@Bean
public Step importStep(
        JobRepository jobRepository,
        PlatformTransactionManager transactionManager,
        ItemReader<Usuario> reader,
        ItemProcessor<Usuario, Usuario> processor,
        ItemWriter<Usuario> writer) {

    return new StepBuilder("importStep", jobRepository)
            .<Usuario, Usuario>chunk(100, transactionManager)
            .reader(reader)
            .processor(processor)
            .writer(writer)
            .build();
}

La declaración:

.<Usuario, Usuario>chunk(100, transactionManager)

indica que el tipo de entrada es Usuario, el tipo de salida también es Usuario y el tamaño del chunk es 100.

El ItemProcessor puede transformar un tipo en otro. Por ejemplo, puedes leer un UsuarioCsv y producir un Usuario listo para persistir.
3. ¿Qué ocurre si falla un chunk?
En un Step transaccional convencional, si una excepción provoca rollback antes del commit, los cambios transaccionales de ese chunk se revierten.

Esto no garantiza que cualquier efecto externo se deshaga: por ejemplo, una petición HTTP que ya se ha enviado no se revierte automáticamente al hacer rollback de la base de datos.

El tamaño del chunk implica una decisión arquitectónica:
- Chunks pequeños: menos elementos por transacción y menor cantidad de trabajo que revertir, pero más commits.
- Chunks grandes: potencialmente menos commits, pero más memoria, transacciones más largas y más trabajo que repetir ante un fallo.
4. Relación con BatchProcessor
En BatchProcessor, imagina una ruta de integración:

CSV → transformación → API → base de datos

Un diseño basado en chunks permite procesar los registros en grupos y controlar la escritura transaccional en la base de datos.

Sin embargo, conviene separar las operaciones externas de las transacciones locales: si la API acepta una petición y después falla la escritura en la base de datos, un reinicio podría repetir esa llamada. Según la API, necesitarás idempotencia, un mecanismo de seguimiento o una estrategia de recuperación.

El tamaño del chunk debe configurarse según el volumen de datos, los recursos disponibles, el comportamiento de los sistemas externos y los requisitos de recuperación.

Pregunta de comprobación
Un Step utiliza chunk(100, transactionManager) y procesa correctamente 100 registros antes de confirmar la transacción. ¿Qué representa el valor 100?

A. El número máximo de Jobs que pueden ejecutarse simultáneamente.

B. El número de registros que se procesan por transacción antes de confirmar el chunk, salvo que termine antes la entrada o intervenga un error.

C. El número de reintentos permitidos ante cualquier error.

D. El número de segundos que puede durar el Step.

ComprobarCorrecto.

La respuesta es B. El tamaño del chunk determina cuántos elementos se agrupan para escribirlos y confirmar la transacción. El último grupo puede ser más pequeño si quedan menos elementos.


---


Fase 3.5 — Spring Batch
Bloque 38: ItemReader, ItemProcessor e ItemWriter
En Spring Batch, estos tres componentes forman el núcleo de un Step basado en chunks. Cada uno tiene una responsabilidad diferenciada, lo que facilita probarlos, reutilizarlos y cambiar una fuente de datos sin reescribir todo el proceso.
1. Responsabilidad de cada componente

ItemReader<T> — Leer

Obtiene un elemento cada vez desde una fuente como un CSV, una base de datos o una API.

Devuelve un elemento o null cuando se termina la entrada.




ItemProcessor<I, O> — Transformar

Recibe un elemento de tipo I y produce uno de tipo O. Puede validar, normalizar o enriquecer datos.

Si devuelve null, el elemento se filtra y no llega al writer.




ItemWriter<O> — Escribir

Recibe una lista de elementos procesados y los escribe en el destino: una base de datos, un archivo u otro sistema.



2. Ejemplo: importar usuarios desde un CSV
Supongamos que el CSV contiene emails y queremos normalizarlos antes de guardarlos.

Procesador

public class UsuarioProcessor
        implements ItemProcessor<UsuarioCsv, Usuario> {

    @Override
    public Usuario process(UsuarioCsv item) {
        String email = item.email().trim().toLowerCase();

        if (email.isBlank()) {
            throw new IllegalArgumentException("Email vacío");
        }

        return new Usuario(email);
    }
}

Este procesador convierte un UsuarioCsv en una entidad Usuario. En este ejemplo, un email vacío provoca una excepción; no se descarta automáticamente.
Lector y escritor
En Spring Batch puedes utilizar componentes ya preparados, por ejemplo:
- FlatFileItemReader<UsuarioCsv> para leer registros de un CSV.
- RepositoryItemWriter<Usuario> para escribir entidades mediante un repositorio Spring Data.
El lector necesita una configuración para interpretar las columnas del CSV, y el escritor debe configurarse con el repositorio correspondiente.

El Step conecta los componentes:

new StepBuilder("importUsuarios", jobRepository)
    .<UsuarioCsv, Usuario>chunk(100, transactionManager)
    .reader(reader)
    .processor(processor)
    .writer(writer)
    .build();

Los genéricos indican que se leen objetos UsuarioCsv y se escriben objetos Usuario.
3. Relación con BatchProcessor
En tu proyecto BatchProcessor, estos componentes permiten separar la lógica de integración:
- Reader: obtiene datos del CSV, la API o la base de datos de origen.
- Processor: transforma los datos según la configuración de la entidad y las reglas de integración.
- Writer: envía los datos a la API o los persiste en la base de datos de destino.
Esta separación permite reutilizar la misma transformación con diferentes lectores o escritores. No obstante, una llamada HTTP externa puede tener efectos que una transacción de base de datos no revierte automáticamente.

Pregunta de comprobación
Un ItemProcessor recibe un registro que debe excluirse del resultado porque no cumple una regla de filtrado. En Spring Batch, ¿qué puede devolver para que ese registro no llegue al ItemWriter?

A. null.


B. RepeatStatus.FINISHED.


C. Un JobParameters vacío.


D. Una nueva instancia del JobRepository.

Correcto.

La respuesta es A: null. Un ItemProcessor puede devolver null para filtrar un elemento. No es lo mismo que lanzar una excepción, que requiere configurar el tratamiento de errores adecuado.

---

Fase 3.5 — Spring Batch
Bloque 39: JobRepository y metadatos
El JobRepository es el componente de Spring Batch que almacena y administra los metadatos de los trabajos y sus ejecuciones. Gracias a él, Spring Batch puede conocer el estado de un proceso, registrar su progreso y gestionar reinicios.

Esto es especialmente importante en BatchProcessor: si una importación de miles de registros falla, necesitas saber qué trabajo se ejecutó, qué etapas completó y qué información se registró para recuperarlo.
1. ¿Qué almacena JobRepository?
Spring Batch mantiene metadatos como estos:
Concepto	Qué representa
JobInstance	Una instancia lógica de un Job, identificada por su nombre y sus parámetros identificadores.
JobExecution	Una ejecución concreta de esa instancia. Una instancia puede tener varias ejecuciones.
StepExecution	El estado y las estadísticas de la ejecución de un Step.
ExecutionContext	Datos de estado que permiten conservar información necesaria para continuar un procesamiento.

Por ejemplo, si ejecutas importUsuarios con los parámetros archivo=usuarios.csv y fecha=2026-10-27, Spring Batch identifica una instancia según los parámetros que sean identificadores.

Si esa instancia falla y vuelves a ejecutarla con los mismos parámetros identificadores, puedes estar intentando reiniciar la misma instancia, en lugar de crear una nueva.
2. ¿Cómo se relacionan estos objetos?
JobInstance

Trabajo lógico + parámetros identificadores

JobExecution

Un intento de ejecución

StepExecution

Estado y estadísticas de cada etapa


El JobRepository persiste estos metadatos, normalmente en tablas específicas de Spring Batch.
3. Configuración de la base de datos de metadatos
Spring Boot puede configurar el repositorio y su infraestructura automáticamente cuando las dependencias y la configuración son adecuadas.

Por ejemplo, en una configuración de desarrollo:

spring.batch.jdbc.initialize-schema=always

Esta propiedad permite inicializar el esquema de metadatos de Spring Batch en los entornos compatibles. No debe activarse indiscriminadamente en producción: la estrategia de creación y evolución del esquema debe controlarse según el entorno y la versión utilizada.

En producción, normalmente se gestiona el esquema mediante migraciones y se conserva la información de metadatos entre reinicios de la aplicación.
4. Aplicación a BatchProcessor
Para tu proyecto, conviene distinguir dos tipos de persistencia:
- Metadatos de Spring Batch: estado de Jobs, ejecuciones, Steps y contextos de recuperación.
- Datos de negocio: entidades importadas, registros transformados y resultados de las integraciones.
No son lo mismo y pueden requerir configuraciones distintas.

Si BatchProcessor utiliza varios DataSource, hay que decidir cuál almacena los metadatos y cuál contiene los datos de negocio. También es importante configurar correctamente los gestores de transacciones: una transacción sobre una base de datos no garantiza que otra base de datos o una API externa se reviertan conjuntamente.

Pregunta de comprobación
Un Job falla y después quieres reanudar la misma instancia utilizando sus parámetros identificadores originales. ¿Qué componente permite a Spring Batch persistir y consultar los metadatos necesarios para gestionar ese reinicio?

A. ItemProcessor.


B. JobRepository.


C. RestController.


D. PasswordEncoder.

Correcto.

La respuesta es B: JobRepository. Conserva los metadatos de las instancias y ejecuciones. Estos datos ayudan a determinar el estado del trabajo y a gestionar su reinicio, siempre que el Job y sus Steps estén configurados para ello.

---

Fase 3.5 — Spring Batch
Bloque 40: Reinicios y estado entre chunks
Una de las ventajas principales de Spring Batch es que permite recuperar un trabajo fallido sin tener que empezar necesariamente desde cero.

Para conseguirlo, combina los metadatos del JobRepository, el estado de los Step y el ExecutionContext.
1. ¿Qué ocurre cuando falla un chunk?
Imagina que BatchProcessor importa 1.000 registros de un CSV, con chunks de 100.
Chunks 1–4

400 registros procesados y confirmados.


Chunk 5

Se produce un error antes del commit y se revierte la transacción.


Reinicio

Spring Batch puede continuar desde el estado guardado, si el Step y sus componentes admiten la recuperación.



No significa que Spring Batch pueda deshacer cualquier operación externa. Si el chunk realizó una petición HTTP que tuvo éxito antes de fallar la transacción de la base de datos, esa petición no se revierte automáticamente.
2. ExecutionContext: guardar el estado
El ExecutionContext permite almacenar datos que el trabajo necesita para continuar después de un fallo.

Por ejemplo, un lector de archivos puede conservar información sobre su posición de lectura.

ExecutionContext context = stepExecution.getExecutionContext();

context.putLong("ultimoRegistro", 400L);

Este código ilustra el almacenamiento de estado; en un lector estándar, normalmente es preferible dejar que el propio componente gestione su posición y su persistencia.

Para que un componente pueda recuperar su estado, debe estar diseñado para ello y guardar la información necesaria en el momento adecuado.
3. Reiniciar una ejecución
En términos generales, un reinicio requiere:
- Que los metadatos anteriores estén disponibles en el JobRepository.
- Que se vuelva a lanzar la misma instancia lógica, con los parámetros identificadores apropiados.
- Que el Job y sus Step permitan continuar desde el estado registrado.
- Que las fuentes de datos sigan siendo compatibles con el punto de recuperación.
Si lanzas el trabajo con parámetros identificadores distintos, puedes crear una nueva JobInstance y comenzar un procesamiento diferente en vez de reanudar el anterior.

Además, el reinicio no garantiza por sí solo que los efectos externos sean exactamente una vez. Para evitar duplicados, puedes necesitar operaciones idempotentes, claves de negocio únicas o registros de seguimiento.
4. Aplicación a BatchProcessor
Para tu proyecto, conviene definir qué debe ocurrir si falla una integración entre CSV, API y base de datos.

Por ejemplo:
- ¿Se reanuda desde el último chunk confirmado?
- ¿Qué sucede si la API aceptó un registro, pero la base de datos falló?
- ¿Cómo se detecta si un registro ya se procesó?
- ¿Qué configuración permite repetir un trabajo con seguridad?
Estas decisiones dependen de los componentes concretos y de los efectos que produzcan. El ExecutionContext ayuda a conservar el progreso, pero no sustituye una estrategia de consistencia para los sistemas externos.

Pregunta de comprobación
Un trabajo ha confirmado cuatro chunks. Durante el quinto se produce un error que provoca rollback. ¿Qué afirmación es correcta?

A. Spring Batch revierte automáticamente todos los chunks anteriores y cualquier petición HTTP.

B. Los chunks anteriores pueden permanecer confirmados; el reinicio depende del estado guardado y de que el trabajo admita recuperación.

C. El trabajo siempre continúa automáticamente desde el quinto chunk, sin configuración adicional.

D. ExecutionContext sustituye al JobRepository y a las transacciones.

Correcto.

La respuesta es B. Los chunks ya confirmados normalmente permanecen guardados. La recuperación depende del estado persistido y de la configuración del trabajo; los efectos externos no se revierten automáticamente.

Bloque 41 — Spring Batch: transacciones y tolerancia a fallos
El objetivo es entender qué se confirma, qué se revierte y cómo puede recuperarse un trabajo cuando falla durante el procesamiento de datos.
1. Transacciones en Spring Batch
En el procesamiento por chunks, Spring Batch agrupa elementos y procesa cada grupo dentro de una transacción.
Leer elementos

ItemReader


Procesar elementos

ItemProcessor


Escribir y confirmar

ItemWriter + commit

Si se produce un error transaccional antes del commit, se puede revertir el chunk actual. Los chunks confirmados anteriormente normalmente permanecen confirmados.

Por ejemplo, con chunk(100), un trabajo procesa 1.000 registros en diez grupos. Si falla el sexto chunk, los cinco anteriores pueden haber quedado confirmados en la base de datos.

Importante: una transacción de base de datos no revierte automáticamente una petición HTTP, un correo enviado o un archivo escrito fuera de esa transacción.
2. Configurar un Step transaccional
Ejemplo simplificado con Spring Batch:

@Bean
Step importStep(
        JobRepository jobRepository,
        PlatformTransactionManager transactionManager,
        ItemReader<Customer> reader,
        ItemProcessor<Customer, Customer> processor,
        ItemWriter<Customer> writer) {

    return new StepBuilder("importStep", jobRepository)
        .<Customer, Customer>chunk(100, transactionManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .build();
}

- chunk(100, transactionManager) establece el tamaño del grupo y el gestor de transacciones.
- El ItemWriter escribe los elementos del chunk.
- El gestor de transacciones coordina el commit o rollback de los recursos transaccionales que administra.
En una aplicación real, comprueba qué recursos participan en la transacción: no todos los sistemas externos comparten la misma transacción.
3. Tolerancia a fallos
Spring Batch permite configurar estrategias para gestionar determinados errores:
- Retry: volver a intentar una operación que ha fallado, por ejemplo, por un error temporal.
- Skip: omitir un elemento que no puede procesarse, cuando la política del negocio lo permite.
- Rollback: revertir la transacción actual cuando corresponda.
- Restart: reanudar un trabajo fallido utilizando el estado persistido, si la configuración lo permite.
Un retry no arregla un error permanente. Por ejemplo, repetir una llamada que siempre recibe un HTTP 400 suele ser inútil; reintentar un HTTP 503 temporal podría tener sentido.
4. Aplicación a BatchProcessor
En tu proyecto, que integra CSV, APIs REST y base de datos, conviene distinguir los fallos según la operación:

| Operación                      | Riesgo                        | Estrategia                                                           |
| ------------------------------ | ----------------------------- | -------------------------------------------------------------------- |
| Leer CSV                       | Fila mal formada              | Validar y, si está permitido, omitirla.                              |
| Consultar una API              | Timeout o HTTP 503            | Aplicar reintentos limitados (retry).                                |
| Validar una entidad            | Datos inválidos               | Registrar el error y aplicar la política de negocio correspondiente. |
| Escribir en BD                 | Error SQL                     | Ejecutar un rollback y, si procede, reiniciar la operación.          |
| Enviar datos a una API externa | Respuesta perdida tras enviar | Diseñar operaciones idempotentes para evitar duplicados.             |

La idempotencia es especialmente importante: ejecutar dos veces una operación debe producir el mismo resultado efectivo que ejecutarla una sola vez. Puedes usar una clave de negocio única, una restricción en la base de datos o un identificador de operación.

En BatchProcessor, no asumiría que un reinicio es seguro hasta comprobar cómo se guardan el progreso, los identificadores procesados y los efectos externos.

Pregunta de comprobación
Un chunk de BatchProcessor falla después de que una API externa haya recibido una petición, pero antes de que la transacción de base de datos se confirme. ¿Qué afirmación es correcta?

A. El rollback de la base de datos deshace automáticamente la petición HTTP.

B. Spring Batch garantiza que la petición HTTP solo se envíe una vez.

C. La base de datos puede revertirse, pero el efecto externo puede persistir; hay que diseñar la recuperación para evitar duplicados.

D. Basta con aumentar el tamaño del chunk para impedir este problema.

Correcto.

El rollback solo afecta a los recursos que participan en la transacción correspondiente. Para recuperarse con seguridad, hay que contemplar reintentos, duplicados e idempotencia.

Bloque 42 — Spring Batch: Skip, Retry y gestión de errores
En Spring Batch, no todos los errores deben tratarse igual. La decisión depende de si el fallo es permanente, temporal o afecta a la integridad de los datos.
1. Skip: omitir registros problemáticos
Se utiliza cuando un elemento no puede procesarse, pero el trabajo puede continuar de forma segura.

Ejemplo en BatchProcessor: un CSV contiene un cliente sin un campo obligatorio. Si las reglas de negocio permiten omitirlo, se puede registrar el error y seguir con los demás registros.
2. Retry: reintentar operaciones fallidas
Se utiliza para errores potencialmente temporales, como un timeout al consultar una API REST.

@Bean
Step importStep(
        JobRepository jobRepository,
        PlatformTransactionManager transactionManager,
        ItemReader<Customer> reader,
        ItemProcessor<Customer, Customer> processor,
        ItemWriter<Customer> writer) {

    return new StepBuilder("importStep", jobRepository)
        .<Customer, Customer>chunk(100, transactionManager)
        .reader(reader)
        .processor(processor)
        .writer(writer)
        .faultTolerant()
        .retry(TransientApiException.class)
        .retryLimit(3)
        .skip(InvalidCustomerException.class)
        .skipLimit(10)
        .build();
}

Este ejemplo configura:
- Hasta 3 intentos para TransientApiException, según la política de reintentos de Spring Batch.
- Hasta 10 elementos omitidos por InvalidCustomerException.
- Si se supera el límite o aparece un error no tolerado, el Step puede fallar.
La configuración exacta debe adaptarse a la versión de Spring Batch y a las excepciones reales de tu aplicación.
3. Clasificar correctamente los errores

Tipo de error	                    Tratamiento habitual
CSV mal formado	                    Skip, si el negocio permite descartar la fila.
Campo obligatorio ausente	        Validar y aplicar Skip si se permite descartar el registro.
HTTP 503 temporal	                Retry limitado, preferiblemente con espera progresiva.
HTTP 400 por datos incorrectos	    No reintentar sin corregir los datos o la solicitud. 
Error SQL de integridad	            Investigar la causa; no omitir automáticamente.
Fallo inesperado de programación	Fallar el Step y corregir el código.

Regla general: utiliza `Skip` para errores de registros que puedan descartarse según las reglas de negocio, `Retry` para errores potencialmente transitorios y la interrupción del proceso para errores que requieran corregir datos, infraestructura o código.

En Spring Batch conviene distinguir, además, entre los errores recuperables de un registro y los errores que deben provocar el fallo del `Step`. La configuración de `skip()` y `retry()` debe ser selectiva: no todas las excepciones de una misma categoría tienen necesariamente el mismo tratamiento.

Importante: un límite de skip no significa que cualquier excepción sea omitible. Spring Batch aplica las políticas de clasificación y tolerancia configuradas. Además, un reintento de una operación externa puede duplicar efectos si la petición anterior llegó a ejecutarse.
4. ¿Cómo registrar los errores?
Para BatchProcessor, interesa registrar el identificador del registro, la causa y el número de intentos, evitando guardar credenciales o datos sensibles innecesarios.

Spring Batch también proporciona mecanismos como SkipListener para reaccionar cuando un elemento se omite y registrar esa decisión.

Por ejemplo, podrías guardar los registros descartados en un fichero de errores o en una tabla de incidencias para poder corregirlos y reprocesarlos posteriormente.

Pregunta de comprobación
BatchProcessor consulta una API REST. A veces recibe HTTP 503, pero también recibe HTTP 400 cuando los datos enviados son inválidos. ¿Qué estrategia es la más adecuada?

A. Reintentar indefinidamente ambos códigos HTTP.

B. Omitir siempre cualquier petición que falle.

C. Reintentar de forma limitada los fallos temporales y corregir o gestionar los datos que provocan el HTTP 400.

D. Aumentar el tamaño del chunk para evitar los errores HTTP.

Correcto.

Los fallos transitorios pueden resolverse mediante reintentos limitados. Un HTTP 400 normalmente exige corregir los datos o gestionar el rechazo, no repetir la misma petición sin cambios.

Bloque 43 — Spring Batch: integración de CSV, APIs REST y base de datos
En BatchProcessor, el objetivo es construir un flujo que lea registros de un CSV, los transforme o valide, consulte o envíe datos mediante una API REST y persista los resultados en una base de datos.
1. Arquitectura del flujo
CSV — ItemReader

Lee una fila y la convierte en un objeto Java

ItemProcessor

Valida, transforma y prepara los datos

Integración REST

Consulta o envía datos a un servicio externo

Base de datos — ItemWriter

Guarda los resultados por chunks


La llamada REST puede situarse en el ItemProcessor o en otro componente de servicio, según las responsabilidades del flujo. No es obligatorio realizarla siempre en esa fase.
2. Leer un CSV
Spring Batch proporciona FlatFileItemReader para leer archivos delimitados.

Ejemplo simplificado de configuración:

@Bean
FlatFileItemReader<CustomerInput> customerReader(
        Resource inputFile) {

    return new FlatFileItemReaderBuilder<CustomerInput>()
        .name("customerReader")
        .resource(inputFile)
        .delimited()
        .names("id", "name", "email")
        .targetType(CustomerInput.class)
        .build();
}

CustomerInput representa cada fila del CSV. La configuración presupone que el archivo tiene las columnas indicadas; el formato real, las cabeceras y los posibles errores deben ajustarse al archivo de entrada.

3. Integrar una API REST
Puedes encapsular la comunicación HTTP en un servicio. Por ejemplo, usando RestClient en versiones de Spring Framework que lo soportan:

@Service
public class CustomerApiClient {

    private final RestClient restClient;

    public CustomerApiClient(RestClient restClient) {
        this.restClient = restClient;
    }

    public CustomerResponse findCustomer(String id) {
        return restClient.get()
            .uri("/customers/{id}", id)
            .retrieve()
            .body(CustomerResponse.class);
    }
}

El RestClient se configura con la URL base y las credenciales que correspondan. También hay que definir cómo tratar los errores HTTP, los timeouts y los reintentos.

Importante: una petición HTTP no queda automáticamente incluida en la transacción de la base de datos. Si el trabajo se reinicia, puede repetir una petición ya ejecutada; considera idempotencia y persistencia del progreso.
4. Persistir los resultados
Un ItemWriter recibe los elementos procesados de un chunk. Para guardar entidades JPA, puedes utilizar un repositorio:

@Component
public class CustomerWriter
        implements ItemWriter<Customer> {

    private final CustomerRepository repository;

    public CustomerWriter(CustomerRepository repository) {
        this.repository = repository;
    }

    @Override
    public void write(
            Chunk<? extends Customer> chunk) {

        repository.saveAll(chunk.getItems());
    }
}

En Spring Batch moderno, ItemWriter recibe un Chunk en lugar de la antigua lista de elementos. El repositorio debe estar configurado para usar la base de datos y el gestor de transacciones adecuados.
5. Decisiones importantes para BatchProcessor
- Configuración externa: ruta del CSV, URL de la API y parámetros de ejecución deben poder configurarse sin modificar el código.
- Validación: separar los datos inválidos de los fallos temporales de comunicación.
- Rendimiento: elegir un tamaño de chunk adecuado y evitar llamadas REST innecesarias.
- Recuperación: definir qué ocurre si falla la escritura después de consultar la API.
- Pruebas: verificar el mapeo del CSV, las respuestas HTTP y la persistencia en la base de datos.
No conviene empezar con paralelismo o chunks enormes antes de asegurar la corrección del flujo y su recuperación ante errores.

Pregunta de comprobación
En BatchProcessor, el CSV se lee correctamente y la API REST responde, pero se produce un error al guardar el chunk en la base de datos. ¿Qué afirmación es correcta?

A. El rollback de la base de datos garantiza que la API REST deshaga su respuesta.

B. La transacción puede revertir la escritura en la base de datos, pero no deshace automáticamente la llamada REST.

C. Spring Batch convierte automáticamente todas las llamadas REST en transacciones distribuidas.

D. La única solución es eliminar el ItemProcessor.

Correcto.

La transacción controla los recursos que participan en ella. Para evitar efectos duplicados al reiniciar, la integración REST debe diseñarse teniendo en cuenta la idempotencia y la recuperación.

Bloque 44 — Spring Batch: pruebas de Jobs y Steps
El objetivo es comprobar que un trabajo de Spring Batch procesa correctamente los datos, gestiona los errores y mantiene el estado esperado cuando se ejecuta o se reinicia.

En BatchProcessor, no basta con probar individualmente el lector CSV o el cliente REST: también hay que comprobar que el flujo completo conecta correctamente las distintas fases.
1. Tipos de pruebas
Tipo	Qué comprueba	Ejemplo en BatchProcessor
Unitarias	Un componente aislado	Validación de una entidad
De Step	Una etapa de Spring Batch	Leer CSV y guardar registros
De Job	El flujo completo	CSV → procesamiento → base de datos
De integración	La colaboración con sistemas reales o de prueba	API HTTP simulada y BD de prueba

2. Probar un Job con Spring Batch Test
Spring Batch ofrece spring-batch-test, que incluye utilidades como JobLauncherTestUtils.

Dependencia Maven, utilizando la versión gestionada por Spring Boot:

<dependency>
    <groupId>org.springframework.batch</groupId>
    <artifactId>spring-batch-test</artifactId>
    <scope>test</scope>
</dependency>

Una prueba simplificada de un Job podría ser:

@SpringBatchTest
@SpringBootTest
class CustomerImportJobTest {

    @Autowired
    private JobLauncherTestUtils jobLauncherTestUtils;

    @Test
    void jobShouldCompleteSuccessfully() throws Exception {
        JobExecution execution =
            jobLauncherTestUtils.launchJob(
                new JobParametersBuilder()
                    .addString("inputFile", "test.csv")
                    .addLong("run.id", System.nanoTime())
                    .toJobParameters()
            );

        assertEquals(
            BatchStatus.COMPLETED,
            execution.getStatus()
        );
    }
}

Este ejemplo comprueba el estado final del Job. Para que sea una prueba fiable, el contexto debe contener el Job correcto, el archivo de prueba debe existir y los recursos de persistencia deben estar configurados.

El parámetro único permite lanzar una nueva instancia del Job cuando corresponda; no significa que debas añadir parámetros únicos indiscriminadamente en producción, donde pueden impedir un reinicio de la misma instancia.
3. Comprobar el resultado, no solo el estado
Que un Job termine con COMPLETED no garantiza que haya importado los datos esperados.

En BatchProcessor, también comprobaría:
- Número de registros leídos, procesados, omitidos y escritos.
- Contenido final de la base de datos.
- Tratamiento de filas inválidas.
- Comportamiento ante un error HTTP.
- Recuperación después de un fallo.
- Ausencia de registros duplicados al reiniciar.
Para probar un Step de manera aislada, puedes utilizar launchStep("customerImportStep") mediante JobLauncherTestUtils, siempre que ese Step esté correctamente registrado y disponible en el contexto.
4. Simular una API REST
Las pruebas no deberían depender de una API externa real, porque puede estar caída, limitada o cambiar sus datos.

Puedes simular las respuestas HTTP para comprobar casos como:
- 200 OK: respuesta válida.
- 400 Bad Request: datos rechazados.
- 503 Service Unavailable: fallo potencialmente temporal.
- Timeout: comportamiento ante una respuesta que no llega.
La prueba debe verificar que el trabajo aplica la política configurada: reintenta, omite un registro o falla según corresponda.

Criterio profesional: las pruebas de integración deben verificar resultados observables y estados persistidos, no limitarse a comprobar que ciertos métodos fueron llamados.

Pregunta de comprobación
Una prueba de BatchProcessor confirma que el Job termina con estado COMPLETED, pero no comprueba la base de datos. ¿Cuál es la principal limitación?

A. Un Job de Spring Batch no puede probarse con JUnit.

B. El estado COMPLETED garantiza que todos los registros se hayan guardado correctamente.


C. La prueba no demuestra que los datos esperados se hayan persistido ni que el resultado sea correcto.

D. Es obligatorio utilizar una API REST real en todas las pruebas.

C

Correcto.

El estado final es solo una parte de la verificación. Hay que comprobar también los registros escritos, las métricas del procesamiento y los escenarios de error relevantes.

---

Bloque 45 — Spring Batch: configuración dinámica y decisiones arquitectónicas
Este bloque cierra la ruta de Spring Batch. En BatchProcessor, la cuestión principal es conseguir que el mismo código pueda ejecutar distintas importaciones sin recompilar la aplicación, manteniendo la recuperación, la integridad de los datos y la capacidad de probar el flujo completo.
1. Configuración externa
No conviene fijar en el código rutas de CSV, URLs, credenciales ni tamaños de chunk. Spring Boot permite configurarlos mediante application.yml, variables de entorno o perfiles.

batch:
  input-file: ${BATCH_INPUT_FILE:./data/customers.csv}
  chunk-size: ${BATCH_CHUNK_SIZE:100}

api:
  base-url: ${CUSTOMER_API_URL:http://localhost:8081}

  Puedes agrupar esos valores en una clase de configuración tipada:

  @ConfigurationProperties(prefix = "batch")
public record BatchProperties(
    String inputFile,
    int chunkSize
) {}

Regístrala con @ConfigurationPropertiesScan o @EnableConfigurationProperties(BatchProperties.class).

Distinción importante: la configuración de la aplicación y los JobParameters tienen propósitos distintos.
- Configuración externa: define cómo se ejecuta la aplicación, por ejemplo, la URL de una API.
- JobParameters: identifica y parametriza una ejecución concreta, por ejemplo, el fichero que se va a importar.
En BatchProcessor, si quieres recuperar una ejecución fallida, debes conservar los parámetros que identifican esa instancia del Job.
2. Rutas de integración
No todas las importaciones tienen por qué seguir el mismo flujo. Por ejemplo:
- CSV → validación → base de datos.
- CSV → API REST → base de datos.
- Base de datos → transformación → API REST.
Si los flujos son sustancialmente distintos, puedes definir varios Jobs o Steps y seleccionar cuál ejecutar mediante configuración o parámetros.

Evita construir una arquitectura excesivamente genérica para tres flujos sencillos. Conviene abstraer cuando existan diferencias reales en las fuentes, las transformaciones o los destinos.
3. DataSource y gestores de transacciones
Un DataSource proporciona conexiones a una base de datos. Un PlatformTransactionManager controla las transacciones de los recursos que administra.

En una aplicación sencilla, Spring Boot puede configurar ambos automáticamente. Si BatchProcessor utiliza una base de datos de negocio y otra para los metadatos de Spring Batch, debes decidir qué DataSource utiliza cada componente.
Base de datos de negocio

Clientes, importaciones y resultados de negocio.

Base de datos de metadatos de Batch

Jobs, Steps, estados de ejecución y contexto persistido.

Pueden compartir base de datos o estar separadas. La configuración afecta a la persistencia del estado y a la recuperación.

Si ambas bases de datos son distintas, no debes asumir que una transacción ordinaria confirma o revierte ambas de forma atómica. Esa coordinación requiere un diseño específico.
4. Reinicios y recuperación
Para que un Job pueda recuperarse después de un fallo, hay que considerar:
- Persistencia de los metadatos de Spring Batch.
- Estado guardado en ExecutionContext, cuando corresponda.
- Identidad estable de la instancia mediante sus JobParameters.
- Configuración de reinicio del Job y sus Steps.
- Idempotencia de las operaciones externas.
- Tratamiento de los registros ya confirmados.
En BatchProcessor, si el Job consulta una API y después escribe en una base de datos, un reinicio puede repetir la consulta. Si además envía datos a otra API, necesitas contemplar que la operación externa haya tenido éxito aunque la aplicación no llegara a guardar ese resultado localmente.
5. Pruebas end-to-end
Una prueba end-to-end debe verificar el flujo desde la entrada hasta el resultado persistido, utilizando dependencias reales o controladas de manera explícita.

Para BatchProcessor, comprobaría como mínimo:
1. Crear un CSV de prueba con registros válidos e inválidos.
2. Ejecutar el Job con parámetros conocidos.
3. Simular las respuestas de la API REST.
4. Verificar los registros y errores guardados en la base de datos.
5. Provocar un fallo y volver a ejecutar la misma instancia cuando proceda.
6. Confirmar que el reinicio no duplica efectos ni pierde datos.

Pregunta de comprobación final
BatchProcessor utiliza una base de datos para los metadatos de Spring Batch y otra para los datos de negocio. El Job falla después de realizar una operación en una API externa. ¿Qué decisión arquitectónica es la más correcta?

A. Asumir que el rollback de la base de datos de metadatos revierte también la base de negocio y la API.

B. Usar siempre los mismos JobParameters para todas las importaciones, independientemente del fichero.


C. Configurar explícitamente las bases de datos y sus gestores de transacciones, persistir el estado necesario y diseñar la recuperación de operaciones externas.

D. Eliminar el JobRepository para que el reinicio sea automático.

Correcto.

Los recursos independientes no forman automáticamente una única transacción. La arquitectura debe definir qué estado persiste cada base de datos y cómo se recuperan los efectos externos.

---

Con esto queda cubierta la ruta marcada de Spring Batch. El siguiente paso útil es comprobar que puedes aplicar estos conceptos a un escenario real de BatchProcessor, especialmente en transacciones, reinicios y pruebas.









--------










A se revierte el chunk que a fallado, 

B para el reincio jobrepository cumple el papel de albergar la informacion realmente persistida, el ultimo chunk al haber fallado no deberia haberse persistido , executioncontext es la implementacion que ofrece springbatch para especificar como se actua ante un fallo. y jopparameters sirve para identificar una ejecucion completa



Corrección — Pregunta 1: recuperación de Spring Batch
Tu respuesta demuestra que entiendes la base de las transacciones y la función general de los componentes de Spring Batch. Sin embargo, hay una imprecisión importante en ExecutionContext y falta responder al apartado C.
Evaluación por apartados
A. Transacciones
Correcto, con matices
El rollback revierte los cambios del chunk actual en los recursos que participan en esa transacción. Los cuatro chunks anteriores, si ya se confirmaron, normalmente permanecen persistidos.

La respuesta de la API REST no se revierte automáticamente: es un efecto externo.



B. JobRepository y JobParameters
Correcto, con matices
- JobRepository: almacena los metadatos de las ejecuciones, incluidos estados de Jobs y Steps, y permite gestionar su ciclo de vida y recuperación.
- JobParameters: identifica la instancia del Job junto con su nombre; no identifica por sí solo una ejecución individual. Una misma instancia puede tener varias ejecuciones.
- El chunk fallido no debería tener sus cambios de negocio confirmados si el rollback se ejecutó correctamente. Los metadatos y los datos de negocio no necesariamente comparten la misma transacción.



ExecutionContext
Incorrecto parcialmente
No es el componente que especifica cómo actuar ante un fallo. Es un mecanismo de almacenamiento de estado que permite a un Job o Step guardar información necesaria para continuar después, por ejemplo, una posición de lectura.

La política de reintentos, omisiones y reinicio se configura mediante los mecanismos correspondientes de Spring Batch. El estado del ExecutionContext debe persistirse correctamente para ser útil durante la recuperación.



C. API REST e idempotencia
Pendiente
No has respondido este apartado. Es fundamental porque la API puede haber realizado la operación aunque posteriormente falle la escritura en la base de datos.



Tu siguiente respuesta
No avanzaremos todavía a la siguiente pregunta. Completa únicamente el apartado C:

Si BatchProcessor vuelve a ejecutar una petición a la API REST durante el reinicio, ¿qué harías para evitar que esa operación produzca efectos duplicados?

Piensa en una clave idempotente, una operación de actualización frente a una creación, o algún mecanismo que permita reconocer que la operación ya se realizó. Explica qué solución elegirías y por qué.

saltar los duplicados

La idea va en la dirección correcta, pero saltar duplicados no garantiza por sí solo que no se dupliquen los efectos en la API. Depende de dónde detectes el duplicado y de cuándo se haya producido la operación.

Por ejemplo, si la API ya ha creado un cliente, pero BatchProcessor falla antes de guardar la respuesta en su base de datos, al reiniciar puedes volver a solicitar la creación.

Una solución más robusta sería:
- Clave idempotente: enviar un identificador único de operación para que la API reconozca las repeticiones y no vuelva a ejecutar el efecto.
- Detección de duplicados: comprobar un identificador de negocio o imponer una restricción única en la base de datos.
- Reintentos seguros: diseñar el flujo para que repetir una operación no provoque efectos adicionales.
Tu respuesta es parcialmente correcta: detectar y saltar duplicados puede servir, pero necesitas saber si el efecto externo ya se produjo y cómo identificarlo de forma fiable.
Pregunta 1 — Cierre del apartado C
Supón que no puedes modificar la API REST, por lo que no admite claves idempotentes. La API crea un cliente y responde correctamente, pero BatchProcessor falla antes de guardar ese cliente en su propia base de datos.

¿Qué harías para reducir el riesgo de duplicar la creación al reiniciar? Explica qué comprobarías y qué limitación tendría tu solución.

comprobar un identificador de negocio e imponer una restricción única en la base de datos. Reintentos seguros: diseñar el flujo para que repetir una operación no provoque efectos adicionalesm, si los provoca capturarlos mediante execution conterxt paraa poder tener en cuenta esa informacion

Tu respuesta mejora respecto a la anterior. Identificas dos mecanismos válidos, pero hay una confusión importante sobre `ExecutionContext`.

## Corrección del apartado C

1\. Identificador de negocio y restricción única: correcto.

Una restricción `UNIQUE` en la base de datos impide insertar dos registros con el mismo identificador. Sin embargo, esto protege tu base de datos local; no impide por sí solo que la API externa cree dos clientes.

2\. Reintentos seguros: correcto como objetivo.

Hay que diseñar el flujo para que repetir una operación no produzca efectos adicionales. Si la API no admite idempotencia, necesitas comprobar si existe alguna forma de consultar el resultado de la operación anterior.

3\. `ExecutionContext`: parcialmente incorrecto.

Puedes utilizarlo para guardar estado relevante para la recuperación, como una posición de lectura o un identificador de progreso. Pero no garantiza que una operación HTTP se haya ejecutado una sola vez.

Si la API creó el cliente y el proceso falló antes de guardar ese hecho localmente, el `ExecutionContext` podría no contener esa información. Existe una ventana de fallo entre ambos sistemas.

### ¿Qué haría en producción?

1. Utilizar un identificador de negocio estable para cada cliente.
2. Consultar la API para comprobar si el cliente ya existe, si ofrece esa posibilidad.
3. Aplicar una restricción única en la base de datos local.
4. Persistir el progreso y diseñar una estrategia de reconciliación para los casos en los que no pueda determinarse si la operación externa tuvo éxito.

Sin idempotencia en la API ni una forma fiable de consultar el resultado, no puedes garantizar que nunca haya duplicados. Solo puedes reducir el riesgo y detectar o reparar inconsistencias.

## Resultado de la pregunta 1

## Pregunta superada con matices

Has identificado correctamente el rollback del chunk, el papel general del `JobRepository` y el uso de restricciones únicas. Debes afianzar la diferencia entre el estado persistido por Spring Batch y los efectos que ya han ocurrido en sistemas externos.

## Pregunta 2 — Concurrencia y Spring Batch

BatchProcessor procesa clientes en paralelo utilizando un pool de hilos. Dos tareas leen simultáneamente el mismo cliente, ambas comprueban que todavía no existe en la base de datos y las dos intentan insertarlo.

La base de datos tiene una restricción `UNIQUE` sobre el identificador del cliente.

¿Qué puede ocurrir y cómo diseñarías la solución para mantener la integridad de los datos?

Explica tu razonamiento. Puedes mencionar transacciones, restricciones únicas, concurrencia o control de errores, pero no necesitas escribir código todavía.

pude darse error por intentar escribir una pila que ya esta en la base de datos deberia gestionarse de manera que esto no afecte a la transaccion mediante una restriccion

Tu respuesta es parcialmente correcta. Has identificado el problema principal: dos hilos pueden intentar insertar el mismo cliente y uno de ellos puede recibir una violación de la restricción UNIQUE.

Hay dos matices importantes.
1. La restricción UNIQUE no evita el error; evita los datos duplicados
La base de datos garantiza la unicidad incluso si las dos tareas comprueban simultáneamente que el cliente no existe. Una de las inserciones podrá completarse y la otra fallará.

Por tanto, no basta con comprobar previamente si el cliente existe: ambas tareas podrían obtener el mismo resultado antes de insertar.
2. ¿Cómo gestionar el error?
Depende del comportamiento que quieras:
- Si el duplicado es válido y esperado: utiliza una operación de inserción que gestione el conflicto de forma segura, según las capacidades de la base de datos.
- Si el duplicado indica un problema: registra el error y no lo ocultes.
- Si utilizas Spring Batch: ten cuidado con las excepciones que provocan rollback. Capturar una excepción Java no garantiza que la transacción siga siendo válida ni que pueda confirmarse.
La restricción de unicidad debe mantenerse como última garantía de integridad. La gestión de conflictos debe diseñarse para que no deje el chunk en un estado inconsistente.
Pregunta 3 — Transacciones y concurrencia
En un ItemWriter, procesas un chunk de 100 clientes. Se insertan correctamente 80, pero el cliente número 81 viola una restricción UNIQUE. El ItemWriter lanza una excepción y la transacción del chunk se revierte.

¿Qué sucede con las primeras 80 inserciones y qué tendría que ocurrir para que el trabajo pudiera continuar sin perder la integridad de los datos?

Explica tu razonamiento. No avances a otra pregunta hasta que respondas.

podria capturarse esas primeras 80 insercciones en el execution context para que la transaccion execute desde ese punto y comfigurar itemwriter para que salte los duplicados

Tu respuesta tiene una parte correcta: configurar el `ItemWriter` para gestionar los duplicados puede ser una solución válida. Sin embargo, guardar las primeras 80 inserciones en el `ExecutionContext` para continuar desde ahí no es lo correcto en este escenario.

## Corrección técnica

### 1. ¿Qué ocurre con las primeras 80 inserciones?

Si las 80 inserciones pertenecen a la misma transacción y esta se revierte correctamente, las 80 también se deshacen. No quedan guardadas en la base de datos.

El rollback afecta a toda la transacción, no solo a la operación número 81.

### 2. ¿Para qué sirve `ExecutionContext`?

Permite persistir estado de ejecución para facilitar la recuperación, como una posición de lectura o un dato de progreso. No conserva automáticamente las inserciones revertidas ni permite reanudar una transacción desde una operación intermedia.

### 3. ¿Cómo resolverlo correctamente?

Depende de si los duplicados son errores esperados o indican un problema de datos.

- Si los duplicados son válidos y esperados, puedes gestionar el conflicto de forma controlada en la base de datos o en el `ItemWriter`.
- Si el duplicado debe provocar un fallo, deja que la excepción se propague y aplica la política de errores correspondiente.
- Si necesitas que Spring Batch omita elementos problemáticos, puedes configurar `skip` para la excepción adecuada, teniendo en cuenta cómo se comporta el escritor y la transacción.

Por ejemplo, una estrategia de inserción que ignore conflictos de unicidad puede evitar que una inserción duplicada aborte el chunk, siempre que sea apropiada para tu base de datos y tu lógica de negocio.

Matiz importante: no captures cualquier excepción y continúes sin más. La transacción podría haber quedado marcada para rollback, y ocultar el error podría producir resultados incorrectos.

## Pregunta 3 — Resultado

Has identificado una solución posible para los duplicados, pero debes distinguir entre gestionar el conflicto de escritura y recuperar el estado transaccional.

Vamos a comprobar ese punto antes de avanzar:

Si la inserción número 81 provoca rollback y las primeras 80 se revierten también, ¿qué debería hacer Spring Batch para procesar correctamente los registros sin perder los válidos?

A. Restaurar las primeras 80 inserciones desde `ExecutionContext`.

B. Reintentar el mismo chunk indefinidamente sin cambiar nada.

C. Aplicar una política de errores adecuada —por ejemplo, `skip` cuando esté justificado— para aislar el elemento problemático y permitir que los válidos se procesen de forma transaccional.

D. Desactivar la restricción `UNIQUE`.


C

Correcto: C.

La idea es aislar el registro problemático sin perder la integridad de los registros válidos. Sin embargo, hay un matiz importante: configurar skip no garantiza por sí solo que el escritor pueda recuperarse de cualquier error.

Si el ItemWriter intenta escribir los 100 registros en una única transacción y el registro 81 provoca un rollback, las primeras 80 inserciones también se revierten. Spring Batch debe aplicar una estrategia de tolerancia a fallos compatible con el escritor y la transacción para identificar el registro problemático y procesar correctamente los demás.

Punto clave: ExecutionContext guarda estado de ejecución; no recupera las inserciones que una transacción ha revertido.
Pregunta 4 — Testing con JUnit y Mockito
En BatchProcessor, tienes un servicio que consulta una API REST y transforma la respuesta en una entidad que posteriormente guarda un repositorio.

Quieres probar el servicio unitariamente, sin realizar peticiones HTTP reales ni acceder a una base de datos.

¿Cómo diseñarías esa prueba utilizando JUnit y Mockito? Indica qué dependencias simularías, qué comportamiento configurarías y qué verificarías al terminar la ejecución.

simularia las dependencias de la api, osea el repo y la BD el comportamiento seria procesar datos de prueba  para ello usaria junit y mockito

Tu respuesta es parcialmente correcta. Has propuesto `synchronized`, que puede resolver el problema, pero la causa que describes no es exactamente la que ocurre en el código.

## Corrección técnica

### 1. ¿Por qué ocurre?

El problema no es que ambos hilos ejecuten el mismo registro, sino que `processed++` no es una operación atómica.

En realidad, implica tres pasos conceptuales:

1. Leer el valor actual de `processed`.
2. Incrementarlo.
3. Escribir el nuevo valor.

Dos hilos pueden leer el mismo valor antes de que ninguno escriba el resultado. Una de las actualizaciones se pierde. Esto se conoce como race condition.

### 2. ¿Cómo solucionarlo?

Opción A — `synchronized`:

```
private int processed = 0;

public synchronized void process() {
    processed++;
}
```

Esto hace que solo un hilo a la vez pueda ejecutar ese método sobre la misma instancia del objeto.

Opción B — `AtomicInteger`:

```
private final AtomicInteger processed =
    new AtomicInteger(0);

public void process() {
    processed.incrementAndGet();
}
```

`AtomicInteger` proporciona un incremento atómico sin necesidad de sincronizar explícitamente el método.

Para un contador compartido sencillo, normalmente elegiría `AtomicInteger`. Si necesitas proteger varias operaciones que deben ejecutarse conjuntamente, `synchronized` o un `Lock` pueden ser más apropiados.

### Evaluación

- Identificación de una solución válida: correcta.
- Explicación de la condición de carrera: incompleta.
- Elección de la herramienta: adecuada, aunque depende del contexto.

## Pregunta 6 — `volatile` frente a `synchronized`

En Java, tienes este campo compartido:

```
private volatile boolean running = true;
```

Un hilo comprueba `running` dentro de un bucle y otro hilo puede cambiarlo a `false`.

¿Por qué `volatile` puede ser suficiente para que el primer hilo observe el cambio, pero no sería suficiente para proteger el contador `processed++` del ejercicio anterior?

no se la respuesta

Vamos a descomponerlo. Es una distinción fundamental en concurrencia de Java.

## 1. ¿Qué hace `volatile`?

Cuando una variable se declara `volatile`, los cambios que escribe un hilo son visibles para los demás hilos que leen esa variable.

```
private volatile boolean running = true;

public void execute() {
    while (running) {
        // Trabajo
    }
}
```

Si otro hilo ejecuta:

```
running = false;
```

el hilo que ejecuta el bucle podrá observar el cambio y salir de él.

Sin `volatile`, el hilo podría seguir leyendo un valor almacenado en caché y no observar oportunamente la actualización.

## 2. ¿Por qué no basta para `processed++`?

Porque `volatile` garantiza visibilidad, pero no convierte una operación compuesta en atómica.

```
private volatile int processed = 0;

public void process() {
    processed++;
}
```

Aunque el campo sea `volatile`, dos hilos todavía pueden leer el mismo valor, incrementarlo y escribir el mismo resultado. Se pierde una actualización.

Para solucionarlo, puedes usar:

- `AtomicInteger`, que ofrece incrementos atómicos.
- `synchronized`, que protege la operación mediante exclusión mutua.

## Diferencia que debes recordar

| Mecanismo       | Visibilidad entre hilos           | Incremento atómico                 |
| --------------- | --------------------------------- | ---------------------------------- |
| `volatile`      | Sí                                | No                                 |
| `synchronized`  | Sí                                | Sí, dentro de la sección protegida |
| `AtomicInteger` | Sí, mediante operaciones atómicas | Sí                                 |

## Pregunta 6 — Segundo intento

Dos hilos comparten una variable `volatile boolean running`. Uno cambia su valor a `false` y el otro lo consulta en un bucle.

¿Por qué `volatile` es suficiente para este caso, pero no para `processed++`?

A. Porque `volatile` hace que todas las operaciones sobre cualquier variable sean atómicas.

B. Porque leer y escribir un booleano es una operación simple cuya visibilidad importa, mientras que `processed++` combina lectura, incremento y escritura.

C. Porque `volatile` bloquea todos los demás hilos hasta que termina el bucle.

D. Porque `volatile` solo funciona con variables booleanas.

Comprobar respuesta

B

Correcto.

`volatile` garantiza la visibilidad de la actualización, pero no hace atómico un incremento compuesto. Esa es la diferencia esencial.

Continuar evaluación

## Pregunta 7 — Spring Batch: recuperación y transacciones

Vamos a reforzar la diferencia entre el estado persistido y los cambios transaccionales, que ha sido uno de los puntos más difíciles en las preguntas anteriores.

### Escenario: BatchProcessor

Un `Step` procesa chunks de 100 clientes. Los primeros tres chunks terminan correctamente. En el cuarto, se insertan 60 clientes y, al guardar el cliente número 61, se produce una excepción que provoca el rollback.

La transacción del chunk funciona correctamente y las inserciones se realizan en la misma transacción de base de datos.

¿Qué ocurre con esos 60 clientes y cómo debería continuar el procesamiento?

A. Los 60 clientes permanecen guardados y Spring Batch continúa desde el cliente 61 gracias al `ExecutionContext`.

B. Los 60 clientes se revierten junto con el resto del chunk; Spring Batch debe gestionar el fallo mediante la política configurada y volver a procesar los registros necesarios.

C. El rollback elimina también los clientes de los tres chunks anteriores.

D. El `JobRepository` recupera automáticamente los 60 clientes y los inserta de nuevo sin repetir el procesamiento.

Comprobar respuesta

Correcto.

El rollback revierte las operaciones del chunk actual que participan en esa transacción. Los tres chunks anteriores permanecen confirmados. El reinicio o la recuperación dependen de la configuración del Step, del estado persistido y de la política de errores; no se garantiza continuar exactamente desde el cliente 61.

Continuar a la pregunta 8

## Pregunta 8 — Testing: Mockito y aislamiento de dependencias

Tema: Testing en Java. Vamos a comprobar que sabes diseñar una prueba unitaria útil, no solo utilizar JUnit y Mockito.

### Escenario: BatchProcessor

Tienes este servicio de Spring Boot:

```
@Service
public class CustomerService {

    private final CustomerApiClient apiClient;
    private final CustomerRepository repository;

    public CustomerService(
            CustomerApiClient apiClient,
            CustomerRepository repository) {
        this.apiClient = apiClient;
        this.repository = repository;
    }

    public Customer importCustomer(String id) {
        CustomerDto dto = apiClient.findCustomer(id);

        Customer customer = new Customer(
            dto.id(), dto.name()
        );

        return repository.save(customer);
    }
}
```

Quieres probar que `importCustomer("42")` transforma correctamente la respuesta de la API y guarda el cliente esperado, sin realizar peticiones HTTP ni acceder a una base de datos real.

¿Cuál sería el enfoque correcto?

A. Crear una base de datos real, llamar a la API y comprobar únicamente que el método no lanza excepciones.

B. Simular `CustomerApiClient` y `CustomerRepository`, configurar sus respuestas con Mockito y verificar el resultado y la entidad enviada al repositorio.

C. Simular solamente `CustomerService`, porque es la clase que queremos probar.

D. Utilizar únicamente `@SpringBootTest`, ya que Mockito no permite comprobar argumentos enviados a un repositorio.

Comprobar respuesta

Correcto.

Para una prueba unitaria, el servicio es el objeto real bajo prueba. Los colaboradores se simulan con Mockito; puedes usar `when(...).thenReturn(...)` para preparar su comportamiento y `verify(...)` o `ArgumentCaptor` para comprobar qué se envió al repositorio.

Continuar a la pregunta 9

## Pregunta 9 — Concurrency: `ExecutorService` y condiciones de carrera

Tema: concurrencia en Java. Aplicaremos lo aprendido a un procesamiento de clientes como el de `BatchProcessor`.

### Escenario

Tienes este código:

```
ExecutorService executor =
    Executors.newFixedThreadPool(4);

for (int i = 0; i < 1000; i++) {
    executor.submit(() -> {
        processed++;
    });
}

executor.shutdown();

System.out.println(processed);
```

Suponemos que `processed` es un campo compartido de tipo `int`, inicializado a `0`.

Esperas obtener `1000`, pero el resultado puede ser inferior. Además, el programa puede imprimir el valor antes de que todas las tareas terminen.

¿Qué dos problemas existen en este código y cómo los solucionarías?

A. Solo falta llamar a `shutdown()` después del bucle; eso garantiza que todas las tareas hayan terminado y que el contador sea correcto.

B. Hay una condición de carrera en `processed++` y no se espera la finalización de las tareas; usaría `AtomicInteger` y esperaría la terminación mediante `awaitTermination()` o `Future.get()`.

C. `newFixedThreadPool(4)` impide que las tareas se ejecuten en paralelo; cambiaría el pool por 1000 hilos.

D. Declararía `processed` como `volatile int` y mantendría el código tal cual, porque `volatile` hace atómico el incremento.

Comprobar respuesta

B

Correcto.

`processed++` no es atómico. Además, `shutdown()` impide aceptar nuevas tareas, pero no espera a que terminen. Puedes usar `AtomicInteger` para el contador y `awaitTermination()` para esperar; alternativamente, conservar los `Future` y esperar con `get()`.

Continuar a la pregunta 10

## Pregunta 10 — Testing: verificar rollback y efectos externos

Tema: Testing. Vamos a reforzar las pruebas unitarias con Mockito y el comportamiento ante errores, algo importante al integrar APIs y bases de datos.

Tienes este servicio:

```
@Service
public class CustomerImportService {

    private final CustomerApiClient apiClient;
    private final CustomerRepository repository;

    @Transactional
    public Customer importCustomer(String id) {
        CustomerDto dto = apiClient.findCustomer(id);

        Customer customer = new Customer(dto.id(), dto.name());

        return repository.save(customer);
    }
}
```

Quieres probar qué sucede si `repository.save(customer)` lanza una `RuntimeException`.

¿Cuál de estas afirmaciones es correcta para una prueba unitaria con Mockito?

A. Basta con usar `@InjectMocks` y `@Mock`; la anotación `@Transactional` hará que Mockito revierta automáticamente cualquier cambio en la base de datos simulada.

B. Configuro el repositorio con `when(...).thenThrow(...)` y verifico que se propaga la excepción. Una prueba unitaria con mocks no demuestra por sí sola que Spring haya ejecutado un rollback real.

C. Si el repositorio lanza una excepción, Spring revierte también automáticamente cualquier petición HTTP que haya realizado `apiClient`.

D. Tengo que utilizar siempre `@SpringBootTest` para comprobar que una excepción se propaga; Mockito no permite simular excepciones.

Comprobar respuesta

Correcto.

Con Mockito puedes configurar el mock para lanzar una excepción y comprobar que el servicio la propaga, por ejemplo, con `assertThrows`. Pero `@Transactional` no crea una transacción real cuando pruebas el servicio aislado con mocks. Para verificar el rollback efectivo, necesitas una prueba de integración con Spring y una base de datos transaccional adecuada.

Matiz importante: el rollback de la base de datos tampoco deshace una petición HTTP ya ejecutada. Los efectos externos requieren estrategias específicas, como idempotencia, compensación o reconciliación.

Continuar a la pregunta 11

## Pregunta 11 — Concurrency: visibilidad frente a atomicidad

Tienes este código Java:

```
public class Worker {

    private volatile boolean running = true;
    private int processed = 0;

    public void run() {
        while (running) {
            processed++;
        }
    }

    public void stop() {
        running = false;
    }

    public int getProcessed() {
        return processed;
    }
}
```

Un hilo ejecuta `run()`, mientras otro puede llamar a `stop()` y un tercero puede consultar `getProcessed()`.

¿Cuál es el diagnóstico técnico más preciso?

A. El código es completamente seguro: `volatile` hace que tanto `running` como `processed` sean visibles y que los incrementos sean atómicos.

B. `volatile` permite que el hilo de ejecución observe el cambio de `running`, pero `processed++` no es atómico y el acceso concurrente a `processed` carece de garantías adecuadas de visibilidad.

C. El único problema es que `running` debería ser `AtomicBoolean`; `processed++` es seguro porque solo lo modifica el hilo de `run()`.

D. Hay que declarar todas las variables como `volatile`; así se resuelven tanto las condiciones de carrera como la atomicidad de las operaciones compuestas.

Comprobar respuesta

B

Correcto.

`volatile` garantiza visibilidad y ordenación respecto a esa variable, pero no convierte operaciones compuestas como `processed++` en operaciones atómicas.

Hay dos matices importantes:

- `running`: `volatile` permite que el hilo de `run()` observe el cambio realizado por `stop()`.
- `processed`: aunque solo lo incremente un hilo, otros hilos lo leen concurrentemente. Sin sincronización, esas lecturas no tienen garantías adecuadas de visibilidad. Si varios hilos lo incrementasen, además habría una condición de carrera con posibles incrementos perdidos.

Una solución sencilla para el contador sería `AtomicInteger`, usando `incrementAndGet()` y `get()`. Otra opción es sincronizar los accesos. La elección depende de las operaciones y del nivel de concurrencia requerido.

Continuar a la pregunta 12

## Pregunta 12 — Spring Boot: inyección de dependencias y ciclo de vida

Estás desarrollando una API REST con Spring Boot. Tienes este servicio:

```
@Service
public class OrderService {

    private final OrderRepository repository;

    public OrderService(OrderRepository repository) {
        this.repository = repository;
    }

    public Order findById(Long id) {
        return repository.findById(id)
                .orElseThrow(() ->
                    new OrderNotFoundException(id));
    }
}
```

Y este controlador:

```
@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderService service;

    public OrderController(OrderService service) {
        this.service = service;
    }

    @GetMapping("/{id}")
    public Order findById(@PathVariable Long id) {
        return service.findById(id);
    }
}
```

¿Cómo consigue Spring crear e inyectar `OrderService` y `OrderRepository`, y qué afirmación es correcta?

A. Spring crea las dependencias buscando las clases durante cada petición HTTP; los constructores solo sirven para facilitar las pruebas.

B. `@Service` hace que Spring registre `OrderService` como bean si el paquete está dentro del escaneo de componentes; Spring resuelve su dependencia por constructor. `OrderRepository` normalmente lo proporciona Spring Data JPA mediante una implementación generada en tiempo de ejecución.

C. Spring solo puede inyectar dependencias si se utiliza `@Autowired` explícitamente en cada constructor; sin esa anotación la aplicación no arranca.

D. `@RestController` convierte automáticamente todas las clases del proyecto en beans, por lo que `@Service` y la configuración de Spring Data no son necesarias.

Comprobar respuesta

Correcto.

Spring administra los objetos registrados como beans dentro de su contenedor IoC. Al crear `OrderService`, resuelve `OrderRepository` y lo pasa al constructor. El controlador recibe de igual forma el servicio.

Puntos importantes:

- Inyección por constructor: permite declarar dependencias obligatorias como `final` y facilita las pruebas unitarias.
- `@Autowired`: no es necesario en un constructor único en las versiones modernas de Spring.
- Spring Data JPA: genera un proxy que implementa la interfaz del repositorio; no necesitas escribir manualmente la implementación habitual.
- Escaneo de componentes: la ubicación de las clases respecto al paquete de la clase principal y la configuración de Spring importa. `@Service` por sí sola no registra un bean si la clase queda fuera del escaneo.

Continuar a la pregunta 13

## Pregunta 13 — Spring Batch: reanudación y transacciones

Estás desarrollando un proceso de importación con Spring Batch que lee un CSV y guarda los registros en una base de datos mediante procesamiento por chunks de 100 elementos.

La ejecución procesa correctamente los primeros 300 registros. Al procesar el siguiente chunk, se produce una excepción al guardar el registro 350 y el proceso falla.

¿Qué afirmación describe mejor lo que sucede y cómo funciona una posible reanudación del job?

A. Spring Batch revierte todos los registros desde el primero, porque cada job se ejecuta siempre dentro de una única transacción global.

B. Los primeros 300 registros normalmente permanecen confirmados; el chunk que falla se revierte si sus escrituras participan en la misma transacción. Para reanudar correctamente, el job debe poder reiniciarse y conservar el estado necesario mediante el `JobRepository` y el `ExecutionContext`, según la configuración del step.

C. Spring Batch continúa automáticamente desde el registro 350 en cualquier circunstancia, aunque el job esté configurado como no reiniciable y no se guarde ningún estado de ejecución.

D. El `ExecutionContext` garantiza que todos los efectos externos, como las peticiones HTTP realizadas durante el procesamiento, también se reviertan cuando falla un chunk.

Comprobar respuesta

Correcto.

En el modelo habitual de procesamiento por chunks, cada chunk se procesa y confirma en su propia transacción. Si falla el chunk que contiene el registro 350, los chunks anteriores ya confirmados normalmente no se revierten.

Para que una reanudación funcione:

- `JobRepository`: almacena metadatos y estados de ejecuciones de jobs y steps.
- `ExecutionContext`: permite persistir el estado necesario para continuar, por ejemplo, la posición de lectura, cuando el componente y la configuración lo soportan.
- Reinicio: depende de que el job y el step sean reiniciables y de que se lance la misma instancia lógica del job con los parámetros adecuados.
- Efectos externos: una llamada HTTP no se deshace por el rollback de una transacción de base de datos. Puede ser necesario implementar idempotencia o reconciliación.

El estado guardado ayuda a reanudar el proceso, pero no garantiza por sí solo que todos los efectos secundarios se ejecuten exactamente una vez.

Continuar a la pregunta 14

Vamos a cerrar el examen con tres preguntas más (14, 15 y 16), una por una. Cubriremos los cuatro temas, priorizando los conceptos que hemos estado reforzando. Después te daré una evaluación global con los aciertos, los errores y qué deberías repasar antes de una entrevista técnica.

## Pregunta 14 — Testing: Mockito y aislamiento

Estás probando un servicio que consulta una API externa y guarda el resultado en una base de datos. Quieres comprobar que, cuando la API devuelve un DTO válido, el servicio guarda la entidad correspondiente.

```
public Customer importCustomer(String id) {
    CustomerDto dto = apiClient.findCustomer(id);
    Customer customer = new Customer(dto.id(), dto.name());
    return repository.save(customer);
}
```

Dispones de `CustomerApiClient` y `CustomerRepository`. ¿Cómo plantearías correctamente la prueba unitaria?

A. Creo mocks de ambas dependencias, configuro la respuesta de la API con `when(...).thenReturn(...)`, ejecuto el servicio y verifico con `verify(...)` que se guarda la entidad esperada.

B. Uso mocks, pero no configuro respuestas: Mockito devuelve automáticamente DTO válidos y entidades completas para cualquier llamada.

C. Uso siempre `@SpringBootTest` y una base de datos real; una prueba unitaria no puede comprobar interacciones entre objetos.

D. Simulo el servicio con `@Mock` y pruebo ese mock, porque así compruebo que la lógica de negocio funciona sin depender de infraestructura.

Comprobar respuesta

Correcto.

El servicio debe ser el objeto real que se prueba; sus dependencias se sustituyen por mocks. Configuras los resultados esperados, ejecutas el método y compruebas tanto el resultado como las interacciones relevantes.

Por ejemplo, puedes usar `ArgumentCaptor<Customer>` para capturar la entidad enviada a `repository.save()` y comprobar sus campos. No necesitas arrancar todo Spring para esta prueba unitaria.

Continuar a la pregunta 15

## Pregunta 15 — Spring Boot: transacciones y excepciones

Tienes este servicio en una aplicación Spring Boot con Spring Data JPA:

```
@Service
public class TransferService {

    private final AccountRepository repository;

    public TransferService(AccountRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        Account from = repository.findById(fromId).orElseThrow();
        Account to = repository.findById(toId).orElseThrow();

        from.withdraw(amount);
        to.deposit(amount);

        repository.save(from);
        repository.save(to);

        throw new RuntimeException("Error inesperado");
    }
}
```

Suponiendo que ambos cambios se realizan dentro de la misma transacción de base de datos y que el método se invoca a través del proxy de Spring, ¿qué sucede cuando se lanza la excepción?

A. Spring confirma la transacción antes de propagar la excepción, porque las llamadas a `save()` ya se han ejecutado.

B. Spring revierte la transacción porque `RuntimeException` provoca rollback por defecto; los cambios de ambas cuentas no quedan confirmados.

C. Spring revierte únicamente la cuenta de origen, porque el método modifica dos entidades diferentes.

D. `@Transactional` solo funciona en métodos privados, por lo que aquí no tiene ningún efecto.

Comprobar respuesta

Correcto.

Por defecto, Spring marca la transacción para rollback ante excepciones no comprobadas, como `RuntimeException`, y ante `Error`. Por tanto, si todo participa en la misma transacción, los cambios de ambas cuentas se revierten.

Matiz importante: llamar a `save()` no significa que los cambios ya estén confirmados. La confirmación sucede al completar correctamente la transacción. Las excepciones comprobadas no provocan rollback por defecto, salvo que se configure, por ejemplo, `rollbackFor`.

Continuar a la pregunta 16

## Pregunta 16 — Spring Batch: reintentos e idempotencia

Último ejercicio del examen. Vamos a comprobar si sabes distinguir entre la recuperación de un proceso batch y la prevención de efectos duplicados.

Estás desarrollando un job de Spring Batch que procesa registros de un CSV. Para cada registro:

1. Consulta una API externa.
2. Envía una petición para crear un pedido en esa API.
3. Guarda el identificador devuelto en tu base de datos.

El proceso falla después de que la API haya creado el pedido, pero antes de que tu aplicación guarde el identificador en la base de datos. Al reiniciar el job, se vuelve a procesar ese registro.

¿Cómo abordarías este problema para evitar crear pedidos duplicados?

A. Configuraría `retryLimit(3)` y `skipLimit(0)`. Spring Batch garantiza que una petición externa solo se ejecute una vez aunque el proceso falle.

B. Usaría una transacción `@Transactional` alrededor de la llamada HTTP y la escritura en la base de datos; así el rollback local desharía automáticamente ambas operaciones.

C. Utilizaría una clave de idempotencia estable por pedido, si la API la admite, para que los reintentos no creen otro pedido. También persistiría y reconciliaría el resultado externo, y diseñaría el procesamiento para tolerar reinicios.

D. Guardaría el registro en `ExecutionContext` antes de llamar a la API. Esto garantiza que el efecto externo y la escritura local se confirmen de forma atómica.

Comprobar respuesta

Correcto.

El problema es una ventana de fallo entre dos sistemas: la API ya ha realizado el efecto, pero la aplicación todavía no ha registrado el resultado. Un rollback local no deshace una operación HTTP remota.

La solución más sólida suele combinar:

- Idempotencia: enviar la misma clave estable en los reintentos, si la API garantiza ese comportamiento.
- Persistencia y reconciliación: guardar el estado de procesamiento y consultar la API para recuperar un resultado si se desconoce si la operación terminó.
- Reanudación de Spring Batch: utilizar el `JobRepository` y el `ExecutionContext` cuando corresponda, sin confundirlos con una garantía de ejecución exactamente una vez.

Si la API no admite idempotencia ni permite consultar el resultado de la operación, no puedes garantizar por completo que no haya duplicados usando únicamente Spring Batch y una transacción local.

## Evaluación global del examen

La evaluación se basa en las preguntas y respuestas que han aparecido en esta conversación. Como no has respondido directamente a todas las preguntas anteriores, no sería riguroso asignarte una nota numérica ni afirmar que has acertado o fallado cuestiones que no has contestado.

Aspectos que el examen ha cubierto

- Concurrency: visibilidad de variables, `volatile`, atomicidad, condiciones de carrera y espera de tareas.
- Testing: Mockito, mocks, verificación de interacciones y diferencia entre pruebas unitarias y de integración.
- Spring Boot: inyección por constructor, beans, Spring Data JPA y transacciones.
- Spring Batch: transacciones por chunks, persistencia del estado, reanudación e idempotencia ante efectos externos.

Prioridades de repaso

1. Concurrency: diferencia entre visibilidad y atomicidad; cuándo usar `volatile`, `AtomicInteger`, `synchronized` y `ExecutorService`.
2. Spring Batch: qué persiste `JobRepository`, para qué sirve `ExecutionContext` y qué ocurre cuando falla un chunk.
3. Testing: escribir una prueba con Mockito que configure un resultado, ejecute el servicio real y compruebe el resultado y las interacciones.
4. Spring Boot: explicar el ciclo de inyección de dependencias y razonar sobre rollback, excepciones y límites de las transacciones.

Mi criterio para una entrevista sería pedirte que implementaras un ejemplo pequeño de cada área y que justificaras las decisiones técnicas. Reconocer la respuesta correcta en un test es útil, pero explicar y aplicar los conceptos sin opciones es una prueba más exigente de dominio.