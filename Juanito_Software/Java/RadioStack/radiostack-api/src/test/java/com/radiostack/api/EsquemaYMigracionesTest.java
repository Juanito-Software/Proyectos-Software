package com.radiostack.api;

import com.radiostack.core.domain.Programa;
import com.radiostack.core.port.ProgramaRepository;
import com.radiostack.core.port.UsuarioRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.core.ConnectionCallback;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Uno de los dos tests de RadioStack que arrancan el contexto completo contra
 * PostgreSQL de verdad; el otro es ChatStompEndToEndTest.
 *
 * Cubre el hueco que quedaba despues de 155 tests —los demas no tocan una base
 * de datos real—: las migraciones de Flyway
 * —`V1__init.sql` y `V2__demo_data.sql`— no se ejecutaban en ninguna parte. Si
 * una estuviera rota, el CI seguiria en verde y el fallo aparecia al desplegar.
 *
 * Lo que hace valioso a este test no es lo que afirma, sino lo que tiene que
 * ocurrir para que llegue a afirmarlo. Arrancar el contexto completo contra
 * PostgreSQL encadena tres comprobaciones que ningun test con dobles puede
 * hacer:
 *
 *   1. Flyway aplica las migraciones. Una sentencia invalida aborta el arranque.
 *   2. Hibernate valida el esquema resultante contra las seis entidades, porque
 *      application.yml fija `ddl-auto: validate`. Una columna renombrada en la
 *      entidad y no en la migracion —o al reves— impide arrancar. Esta es la
 *      deriva que ningun test unitario ve: las dos mitades estan bien por
 *      separado y no encajan.
 *   3. El CommandLineRunner de DataInitializer se ejecuta contra ese esquema.
 *
 * Es la misma leccion del `-parameters`: la distancia entre «mis clases
 * funcionan» y «la aplicacion arranca» es donde viven los fallos caros.
 *
 * Por que se salta en local. Estos tests necesitan PostgreSQL escuchando con las
 * credenciales que documenta application.yml. En el CI lo levanta el runner como
 * servicio; en un portatil no tiene por que haberlo, y un `mvn test` que falla
 * por falta de infraestructura acaba enseñando a ignorar los fallos. La marca es
 * la variable RADIOSTACK_DB_TESTS, que solo define el workflow.
 *
 * Y se salta en bloque a proposito: el paso del CI que cuenta tests descuenta los
 * saltados, asi que si esa variable no llegara al job, el recuento bajaria de 165
 * a 155 y el job fallaria. Estos tests no pueden dejar de ejecutarse en silencio.
 */
@SpringBootTest
@EnabledIfEnvironmentVariable(
        named = "RADIOSTACK_DB_TESTS",
        matches = "true",
        disabledReason = "necesita PostgreSQL; el CI lo levanta como servicio del runner")
class EsquemaYMigracionesTest {

    /** Las siete tablas que crea V1__init.sql. */
    private static final List<String> TABLAS = List.of(
            "usuario", "locutor", "programa", "programa_locutor",
            "emision", "comentario", "chat_message");

    @Autowired
    private JdbcTemplate jdbc;

    @Autowired
    private Environment entorno;

    @Autowired
    private ProgramaRepository programaRepository;

    @Autowired
    private UsuarioRepository usuarioRepository;

    @Test
    void el_contexto_arranca_contra_postgresql() {
        // Que este test se ejecute ya significa que Flyway aplico las migraciones
        // y que Hibernate valido el esquema: si cualquiera de las dos cosas
        // fallara, el contexto no habria llegado a existir.
        assertNotNull(jdbc);

        // Y contra PostgreSQL, no contra una base en memoria: si alguien
        // «arreglara» la lentitud de este test cambiandolo a H2, dejaria de
        // probar el SQL que se ejecuta en produccion —BIGSERIAL, TEXT, los
        // REFERENCES con ON DELETE CASCADE— y este test lo impide.
        String motor = jdbc.execute(
                (ConnectionCallback<String>) conexion -> conexion.getMetaData().getDatabaseProductName());
        assertEquals("PostgreSQL", motor);
    }

    @Test
    void la_validacion_del_esquema_esta_activada() {
        // Sin `validate`, arrancar no demostraria nada: Hibernate se limitaria a
        // usar el esquema que encontrase. Con `update` incluso lo corregiria por
        // su cuenta, tapando para siempre la deriva que este test busca.
        //
        // Si alguien cambia esa propiedad, el test de arriba seguiria pasando y
        // habria dejado de comprobar lo que cree comprobar. Este lo impide.
        assertEquals("validate", entorno.getProperty("spring.jpa.hibernate.ddl-auto"));
    }

    @Test
    void flyway_ha_aplicado_las_dos_migraciones_y_ninguna_ha_fallado() {
        List<String> versiones = jdbc.queryForList(
                "select version from flyway_schema_history where success = true order by installed_rank",
                String.class);

        assertTrue(versiones.contains("1"), "no se ha aplicado V1__init.sql: " + versiones);
        assertTrue(versiones.contains("2"), "no se ha aplicado V2__demo_data.sql: " + versiones);
    }

    @Test
    void las_siete_tablas_del_dominio_existen_en_el_esquema() {
        // Comprobarlas por nombre y no por «hay tablas» tiene un motivo: una
        // migracion futura que se deje una tabla sin crear seguiria aplicandose
        // sin error, y Hibernate solo protestaria por las entidades que mapean
        // esa tabla. Aqui la ausencia se ve directamente.
        for (String tabla : TABLAS) {
            Integer existe = jdbc.queryForObject(
                    "select count(*) from information_schema.tables "
                            + "where table_schema = 'public' and table_name = ?",
                    Integer.class, tabla);
            assertEquals(1, existe, "falta la tabla " + tabla);
        }
    }

    @Test
    void los_datos_de_demostracion_de_la_v2_estan_cargados() {
        // V2 inserta en usuario, locutor, programa, programa_locutor y emision.
        // Se comprueba que hay filas, no cuantas: el numero exacto es contenido
        // de demostracion y cambiarlo no deberia romper un test.
        for (String tabla : List.of("usuario", "locutor", "programa", "programa_locutor", "emision")) {
            Integer filas = jdbc.queryForObject("select count(*) from " + tabla, Integer.class);
            assertTrue(filas != null && filas > 0, "la tabla " + tabla + " se quedo vacia tras V2");
        }
    }

    @Test
    void el_administrador_inicial_existe_tras_arrancar() {
        // DataInitializer es un CommandLineRunner: se ejecuta al arrancar y hasta
        // ahora nadie comprobaba que funcionara contra el esquema real. Crea la
        // cuenta con la que se entra por primera vez a una instalacion nueva.
        assertTrue(usuarioRepository.findByEmail("admin@radiostack.local").isPresent(),
                "DataInitializer no ha creado la cuenta de administracion");
    }

    @Test
    @Transactional
    void un_programa_va_y_vuelve_por_el_adaptador_real_contra_la_base_de_datos() {
        // El primer test del proyecto que ESCRIBE en una base de datos de verdad
        // atravesando la pila entera: adaptador, mapeador, Hibernate y PostgreSQL.
        //
        // Los 34 tests de persistence comprueban que el adaptador llama bien a su
        // repositorio, con un doble. Ninguno puede decir si la columna existe, si
        // el tipo encaja o si el id lo genera la secuencia. Esto si.
        //
        // @Transactional revierte al terminar: el test no deja rastro.
        Programa guardado = programaRepository.save(
                new Programa(null, "Programa de prueba", "Creado por el test de esquema", "Test", true));

        assertNotNull(guardado.getId(), "la secuencia de PostgreSQL no ha asignado id");

        Programa leido = programaRepository.findById(guardado.getId()).orElseThrow();
        assertEquals("Programa de prueba", leido.getNombre());
        assertEquals("Creado por el test de esquema", leido.getDescripcion());
        assertTrue(leido.isActivo());
    }
}
