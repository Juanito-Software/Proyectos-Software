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


/**
 * Configuración de la ejecución de trabajos por lotes utilizando Spring Batch.
 * Esta clase configura los componentes principales para ejecutar un trabajo por lotes,
 * incluyendo el repositorio de trabajos, el lanzador de trabajos y la gestión de transacciones.
 */

/*{
    "reader": "databaseItemReader",
    "processor": "genericProcessor",
    "writer": "csvItemWriter"
}*/

//@EnableScheduling
@Configuration
@PropertySource("classpath:application.properties")
public class BatchConfig {

    private final DataSource dataSource;

    public BatchConfig(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    // Configuracion de JdbcTemplate
    @Bean(name = "jdbcTemplate")
    public JdbcTemplate jdbcTemplate() {
        return new JdbcTemplate(dataSource);
    }

    // Configuración de JpaTransactionManager si no estuvieramos usando JPA usariamos PlatformTransactionManager
    //
    // @Primary porque desde que existe secondTransactionManager hay dos beans
    // de este tipo. Todo lo que pida un JpaTransactionManager por tipo -el
    // constructor de BatchController, entre otros- debe recibir el de la base de
    // datos principal; el segundo solo se usa cuando la peticion lo nombra
    // explicitamente.
    @Primary
    @Bean(name = "transactionManager")
    public JpaTransactionManager transactionManager(EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }


    // Configuración del JobRepository
    @Bean(name = "jobRepository")
    public JobRepository jobRepository(JpaTransactionManager transactionManager) throws Exception {
        JobRepositoryFactoryBean factory = new JobRepositoryFactoryBean();
        factory.setDataSource(dataSource);
        factory.setTransactionManager(transactionManager);
        factory.setDatabaseType("MYSQL");
        factory.afterPropertiesSet(); // Inicializa el factory
        return factory.getObject();
    }

    // Configuración de JobLauncher usando TaskExecutorJobLauncher
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
     */
    @Bean(name = "secondDatabaseItemWriter")
    public JpaItemWriter<Object> secondDatabaseItemWriter(
            @Qualifier("secondEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        JpaItemWriter<Object> writer = new JpaItemWriter<>();
        writer.setEntityManagerFactory(entityManagerFactory);
        return writer;
    }

}
