package com.example.BatchProcessor.controller;

import com.example.BatchProcessor.listener.JobCompletionListener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.JobParameters;
import org.springframework.batch.core.JobParametersBuilder;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.launch.JobLauncher;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemProcessor;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.ItemWriter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.ApplicationContext;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Único punto de entrada HTTP: compone y lanza un job de Spring Batch en
 * caliente.
 *
 * <p>No hay jobs declarados en el código. {@code POST /batch/run} recibe los
 * <b>nombres de bean</b> del lector, el procesador y el escritor, los busca en
 * el contexto de Spring, monta con ellos un {@code Step} por chunks y un
 * {@code Job}, y lo lanza. Así se cubren las nueve combinaciones
 * CSV/API/BD → CSV/API/BD sin una clase por cada una.
 *
 * <p>Ejemplo:
 * <pre>
 * POST /batch/run?reader=csvItemReader&amp;processor=genericProcessor&amp;writer=databaseItemWriter
 * </pre>
 *
 * <p>La entidad no viaja en la petición: sale de la propiedad
 * {@code entityClass} y se pasa al job como parámetro, del que la leen los
 * componentes con {@code @StepScope} o con {@code beforeStep}.
 */
@RestController
@RequestMapping("/batch")
public class BatchController {

    private static final Logger log = LoggerFactory.getLogger(BatchController.class);

    /** Lanzador síncrono (ver {@code BatchConfig#jobLauncher}). */
    private final JobLauncher jobLauncher;
    /** Contexto de Spring, del que se sacan los beans por nombre. */
    private final ApplicationContext context;
    /** Gestor de transacciones por defecto: el de la base principal. */
    private final JpaTransactionManager jpaTransactionManager;
    /** Repositorio donde se registran el job y el paso que se crean. */
    private final JobRepository jobRepository;
    /** Escucha que registra en el log el resultado de cada ejecución. */
    private final JobCompletionListener jobCompletionListener;
    /** Nombre completo de la entidad a procesar (propiedad {@code entityClass}). */
    private String entityClass;

    /**
     * @param jobLauncher           lanzador de jobs
     * @param context               contexto de Spring
     * @param jpaTransactionManager gestor de transacciones principal ({@code @Primary})
     * @param jobRepository         repositorio de jobs
     * @param jobCompletionListener escucha de fin de job
     * @param entityClass           valor de la propiedad {@code entityClass}
     */
    public BatchController(JobLauncher jobLauncher, ApplicationContext context, JpaTransactionManager jpaTransactionManager, JobRepository jobRepository, JobCompletionListener jobCompletionListener, @Value("${entityClass}") String entityClass) {
        this.jobLauncher = jobLauncher;
        this.context = context;
        this.jpaTransactionManager = jpaTransactionManager;
        this.jobRepository = jobRepository;
        this.jobCompletionListener = jobCompletionListener;
        this.entityClass = entityClass;
    }

    /**
     * Compone un job con los beans indicados y lo ejecuta hasta el final.
     *
     * <p>Parámetros de la petición (query string o formulario):
     * <ul>
     *   <li>{@code reader}: {@code csvItemReader}, {@code apiItemReader} o
     *       {@code databaseItemReader}.</li>
     *   <li>{@code processor}: {@code genericProcessor}.</li>
     *   <li>{@code writer}: {@code csvItemWriter}, {@code apiItemWriter},
     *       {@code databaseItemWriter} o {@code secondDatabaseItemWriter}.</li>
     *   <li>{@code transactionManager} (opcional): solo hace falta con
     *       {@code secondDatabaseItemWriter}, y entonces debe ser
     *       {@code secondTransactionManager}.</li>
     * </ul>
     *
     * <p>Como el lanzador es síncrono, la respuesta llega cuando el job ya ha
     * terminado. Ojo: un 200 significa que el job se lanzó y terminó de
     * ejecutarse, no que acabara en {@code COMPLETED}; el estado final queda en
     * el log ({@link JobCompletionListener}) y en las tablas {@code BATCH_*}.
     *
     * @param params todos los parámetros de la petición
     * @return 200 si el job se lanzó; 400 si falta alguno de los tres beans
     *         obligatorios; 500 si un bean no existe, no es del tipo esperado o
     *         el lanzamiento falla (el detalle va solo al log)
     */
    @PostMapping("/run")
    public ResponseEntity<String> runBatchJob(@RequestParam Map<String, String> params) {
        try {
            // Obtener los nombres de los componentes desde los parámetros
            String readerBean = params.get("reader");
            String processorBean = params.get("processor");
            String writerBean = params.get("writer");


            // Verificar si los parámetros son válidos
            if (readerBean == null || processorBean == null || writerBean == null) {
                return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                        .body("Debe proporcionar los parámetros 'reader', 'processor' y 'writer'.");
            }

            // Obtener los componentes desde el contexto de Spring
            ItemReader<?> reader = (ItemReader<?>) context.getBean(readerBean);
            ItemProcessor<?, ?> processor = (ItemProcessor<?, ?>) context.getBean(processorBean);
            ItemWriter<?> writer = (ItemWriter<?>) context.getBean(writerBean);

            // Gestor de transacciones del paso.
            //
            // Por defecto el de la base de datos principal, que es lo que
            // necesitan ocho de las nueve rutas. La excepcion es escribir en la
            // segunda base de datos: JpaItemWriter persiste con el
            // EntityManager asociado al gestor que gobierna el paso, asi que
            // escritor y gestor tienen que apuntar a la misma base. Si no
            // coinciden, la escritura falla con "No EntityManager with actual
            // transaction available".
            //
            // Se pide por nombre de bean, igual que los otros tres, en lugar de
            // deducirlo del escritor: una regla implicita en el controlador
            // seria una cosa mas que recordar cada vez que se añada un escritor.
            String transactionManagerBean = params.get("transactionManager");
            PlatformTransactionManager transactionManager =
                    (transactionManagerBean == null || transactionManagerBean.isBlank())
                            ? jpaTransactionManager
                            : context.getBean(transactionManagerBean, PlatformTransactionManager.class);

            // Crear el Step dinámicamente. Procesa por chunks de 10: lee 10
            // elementos, los procesa y los escribe en una sola transacción.
            // Los casts son inevitables: los beans llegan sin tipo genérico
            // desde el contexto, y el tipo real de los elementos (la entidad)
            // solo se conoce en tiempo de ejecución.
            Step dynamicStep = new StepBuilder("dynamicStep", jobRepository)
                    .<Object, Object>chunk(10, transactionManager)  // Tamaño del chunk, puedes ajustarlo
                    .reader(reader)
                    .processor((ItemProcessor<? super Object, ?>) processor)
                    .writer((ItemWriter<? super Object>) writer)
                    .build();

            // Crear el Job dinámicamente
            Job dynamicJob = new JobBuilder("dynamicJob", jobRepository)
                    .start(dynamicStep)
                    .listener(jobCompletionListener)
                    .build();

            // Parámetros del job. entityClass es el que leen lectores y
            // escritores para saber con qué clase trabajar. "Fecha" lleva la
            // marca de tiempo para que cada lanzamiento sea una instancia de
            // job distinta: Spring Batch no vuelve a ejecutar una instancia que
            // ya terminó con los mismos parámetros.
            JobParameters jobParameters = new JobParametersBuilder()        //IMPORTANTE
                    .addString("entityClass", entityClass)
                    .addString("Fecha",  " " + System.currentTimeMillis())  // Añadimos el parámetro del archivo
                    .toJobParameters();

            jobLauncher.run(dynamicJob, jobParameters);

            return ResponseEntity.ok("Job started successfully!");
        } catch (Exception e) {
            // El detalle del error va al log del servidor, no a la respuesta:
            // e.getMessage() puede exponer rutas, consultas SQL o nombres de
            // clases internas a quien llame al endpoint.
            log.error("Error al lanzar el job de batch", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error starting job. Consulte los logs del servidor.");
        }
    }
}