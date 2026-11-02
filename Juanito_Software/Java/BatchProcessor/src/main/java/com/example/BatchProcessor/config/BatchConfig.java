package com.example.BatchProcessor.config;

import com.example.BatchProcessor.reader.DatabaseItemReader;
import jakarta.persistence.EntityManagerFactory;
import org.springframework.batch.core.configuration.annotation.StepScope;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.launch.support.TaskExecutorJobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.repository.support.JobRepositoryFactoryBean;
import org.springframework.batch.item.database.JpaItemWriter;
import org.springframework.batch.item.database.JpaPagingItemReader;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.PropertySource;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.orm.jpa.JpaTransactionManager;

import javax.sql.DataSource;


// Ejemplo de la combinación de beans que recibe /batch/run (como parámetros
// de la petición, no como cuerpo JSON):
/*{
    "reader": "databaseItemReader",
    "processor": "genericProcessor",
    "writer": "csvItemWriter"
}*/

/**
 * Infraestructura de Spring Batch: repositorio de jobs, lanzador, gestor de
 * transacciones principal y los lectores/escritores de base de datos.
 *
 * <p>Aquí <b>no se declara ningún {@code Job}</b>. Los jobs se componen en
 * caliente en {@code BatchController} a partir de los nombres de bean que
 * llegan en la petición; esta clase solo aporta las piezas que ese montaje
 * necesita y los beans que no se pueden registrar por escaneo (los de base de
 * datos, porque dependen de parámetros del job o de una
 * {@code EntityManagerFactory} concreta).
 *
 * <p>Todos los metadatos de Spring Batch (tablas {@code BATCH_*}) viven en la
 * base de datos <b>principal</b>, la del {@code DataSource} que recibe el
 * constructor.
 */
//@EnableScheduling
@Configuration
@PropertySource("classpath:application.properties")
public class BatchConfig {

    /** Base de datos principal: guarda los metadatos de Spring Batch. */
    private final DataSource dataSource;

    /**
     * @param dataSource {@code DataSource} principal (el marcado como
     *                   {@code @Primary} en {@code DatabaseConfig})
     */
    public BatchConfig(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    /**
     * {@code JdbcTemplate} sobre la base principal, para consultas SQL directas
     * fuera de JPA.
     *
     * @return plantilla JDBC ligada al {@code DataSource} principal
     */
    @Bean(name = "jdbcTemplate")
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource);
    }

    /**
     * Gestor de transacciones JPA de la base principal. Si el proyecto no usara
     * JPA bastaría un {@code PlatformTransactionManager} genérico.
     *
     * <p>Es {@code @Primary} porque desde que existe
     * {@code secondTransactionManager} hay dos beans de este tipo. Todo lo que
     * pida un {@code JpaTransactionManager} por tipo —el constructor de
     * {@code BatchController}, entre otros— debe recibir el de la base
     * principal; el segundo solo se usa cuando la petición lo nombra
     * explícitamente.
     *
     * @param entityManagerFactory factoría JPA principal
     * @return gestor de transacciones por defecto de los pasos
     */
    @Primary
    @Bean(name = "transactionManager")
    public JpaTransactionManager transactionManager(EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }


    /**
     * Repositorio de jobs: donde Spring Batch registra cada ejecución, sus
     * parámetros y el estado de cada paso (tablas {@code BATCH_*}).
     *
     * <p>Se fija {@code MYSQL} como tipo de base porque es la de producción; los
     * tests corren sobre H2 en modo compatible, que acepta el mismo SQL.
     *
     * @param transactionManager gestor con el que se guardan esos metadatos
     * @return repositorio ya inicializado
     * @throws Exception si la factoría no puede crear el repositorio
     */
    @Bean(name = "jobRepository")
    public JobRepository jobRepository(JpaTransactionManager transactionManager) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(dataSource);
        factory.setTransactionManager(transactionManager);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet(); // Inicializa el factory
        return factory.getObject();
    }

    /**
     * Lanzador de jobs <b>síncrono</b>: {@code run()} no vuelve hasta que el job
     * termina. Así la respuesta HTTP de {@code /batch/run} ya trae el estado
     * final y los tests pueden comprobar el resultado justo después de lanzar.
     * Cambiar a {@code SimpleAsyncTaskExecutor} lo haría asíncrono.
     *
     * @param jobRepository repositorio donde se registran las ejecuciones
     * @return lanzador configurado
     * @throws Exception por compatibilidad con la firma de Spring Batch
     */
    @Bean(name = "jobLauncher")
    public JobLauncher jobLauncher(JobRepository jobRepository) throws Exception {
        TaskExecutorJobLauncher jobLauncher = new TaskExecutorJobLauncher();
        jobLauncher.setJobRepository(jobRepository);

        // Configura un TaskExecutor (sincrónico o asincrónico)
        TaskExecutor taskExecutor = new SyncTaskExecutor();  // O usa SimpleAsyncTaskExecutor para asincrónico
        jobLauncher.setTaskExecutor(taskExecutor);  // Establecer el TaskExecutor
        return jobLauncher;
    }


    // Los beans de lector, escritor y procesador NO se declaran aqui.
    //
    // Aqui hubo un bloque comentado que los declaraba —csvItemReader,
    // csvItemWriter, apiItemReader, apiItemWriter, genericProcessor y
    // personaItemProcessor—. Estaba desactivado y aun asi la aplicacion
    // funcionaba, porque esas clases llevan @Component y Spring las registra
    // por escaneo con el nombre de la clase en minuscula inicial. Es decir:
    // esa configuracion explicita decia una cosa y el comportamiento real era
    // otro, y quien la leyera se llevaba una idea equivocada de como se
    // resuelven los beans que pide /batch/run.
    //
    // Se ha retirado. Los nombres que acepta el endpoint son los que genera el
    // escaneo: csvItemReader, csvItemWriter, apiItemReader, apiItemWriter y
    // genericProcessor. Los de base de datos -databaseItemReader y
    // databaseItemWriter- se declaran mas abajo como @Bean, porque necesitan
    // parametros del job o la EntityManagerFactory.
    //
    // Antes esta lista incluia tambien personaItemProcessor, que existia para
    // convertir en entidad los mapas que devolvia el lector de API. Ese lector
    // ya deserializa directamente en la entidad, asi que el procesador dejo de
    // hacer falta y se retiro. Si alguna vez una API devuelve una forma
    // distinta de la entidad, hara falta un procesador propio, pero para
    // mapear de verdad y no para compensar el borrado de tipos.


    //DB


    /**
     * El @StepScope no es opcional: sin el, la expresion
     * #{jobParameters['entityClass']} no tiene de donde leer. Devuelve un proxy
     * que se resuelve cuando el paso arranca, y por eso el controlador puede
     * pedir el bean antes de lanzar el job.
     *
     * @param entityManagerFactory factoría JPA de la base principal (origen)
     * @param entityClassName      nombre completo de la entidad a leer, tomado
     *                             del parámetro {@code entityClass} del job
     * @return lector paginado de todas las filas de esa entidad
     * @throws ClassNotFoundException si {@code entityClass} no es una clase
     *                                del classpath
     */
    @Bean(name = "databaseItemReader")
    @StepScope
    public JpaPagingItemReader<?> databaseReader(EntityManagerFactory entityManagerFactory,
                                                 @Value("#{jobParameters['entityClass']}") String entityClassName) throws ClassNotFoundException {
        return new DatabaseItemReader().databaseReader(entityManagerFactory, entityClassName);
    }

    /**
     * Escritor a base de datos, valido para cualquier entidad JPA.
     *
     * <p>Antes era un {@code ManualItemWriter<T extends GenericEntity>} que
     * guardaba con un repositorio de Spring Data. Esa firma ataba el escritor a
     * las entidades que heredaran de {@code GenericEntity}, y era el motivo de
     * que {@code Persona} —una {@code @Entity} independiente— pudiera leerse y
     * escribirse a CSV o a la API pero no guardarse en base de datos.
     *
     * <p>{@code JpaItemWriter} persiste vía {@code EntityManager}, asi que
     * acepta cualquier cosa anotada como {@code @Entity} sin pedir herencia. Con
     * ello desaparece tambien la trampa de las cabeceras: como ya no hace falta
     * heredar de {@code GenericEntity}, deja de importar que
     * {@code getDeclaredFields()} no devuelva los campos heredados.
     *
     * <p>Ojo: {@code JpaItemWriter} hace {@code merge}, así que un id que ya
     * exista en la tabla se <b>actualiza</b> en vez de insertarse (pendiente en
     * el ToDo de {@code MAINTENANCE.md}).
     *
     * @param entityManagerFactory factoría JPA de la base principal (destino)
     * @return escritor que persiste cualquier {@code @Entity}
     */
    @Bean(name = "databaseItemWriter")
    public JpaItemWriter<Object> databaseItemWriter(EntityManagerFactory entityManagerFactory) {
        JpaItemWriter<Object> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }

    /**
     * Escritor a la segunda base de datos.
     *
     * <p>Idéntico al anterior salvo por la {@code EntityManagerFactory} que
     * recibe. Con esto la ruta base de datos → base de datos no necesita ningún
     * componente nuevo: es el lector de siempre, {@code genericProcessor} y este
     * escritor.
     *
     * <p><b>Hay que emparejarlo con su gestor de transacciones.</b> El paso se
     * ejecuta dentro del gestor que reciba el controlador, y este escritor
     * persiste con el {@code EntityManager} de la segunda base. Si el paso usa
     * el gestor de la primera, la escritura falla. Por eso la petición debe
     * incluir {@code transactionManager=secondTransactionManager}.
     *
     * @param entityManagerFactory factoría JPA de la segunda base
     * @return escritor que persiste en la segunda base
     */
    @Bean(name = "secondDatabaseItemWriter")
    public JpaItemWriter<Object> secondDatabaseItemWriter(
            @Qualifier("secondEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        JpaItemWriter<Object> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }

}
