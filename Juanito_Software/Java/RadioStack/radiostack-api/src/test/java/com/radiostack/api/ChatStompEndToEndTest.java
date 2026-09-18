package com.radiostack.api;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.security.JwtService;
import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import com.radiostack.core.service.ChatService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.messaging.converter.MappingJackson2MessageConverter;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompFrameHandler;
import org.springframework.messaging.simp.stomp.StompHeaders;
import org.springframework.messaging.simp.stomp.StompSession;
import org.springframework.messaging.simp.stomp.StompSessionHandler;
import org.springframework.messaging.simp.stomp.StompSessionHandlerAdapter;
import org.springframework.http.converter.json.Jackson2ObjectMapperBuilder;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.web.socket.WebSocketHttpHeaders;
import org.springframework.web.socket.client.standard.StandardWebSocketClient;
import org.springframework.web.socket.messaging.WebSocketStompClient;

import java.lang.reflect.Type;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * El camino completo del chat por STOMP, contra un servidor real.
 *
 * EsquemaYMigracionesTest comprueba que la aplicacion arranca contra
 * PostgreSQL. Este comprueba que, una vez arrancada, el chat funciona de punta a
 * punta: abre un WebSocket de verdad contra el Tomcat embebido, negocia una
 * sesion STOMP, se suscribe y publica en el broker, y termina viendo si el
 * mensaje llega a la base de datos.
 *
 * Ningun test con dobles puede cubrir esto. El muelle de pruebas unitario
 * verificaba que el interceptor rechazara un SEND sin usuario y que el
 * controlador enviara el mensaje, pero nunca que ese interceptor y ese
 * controlador estuvieran conectados entre si por el cable que de verdad los une:
 * el canal entrante del broker, la cabecera Authorization de la trama CONNECT y
 * la suscripcion al topic. Aqui, si una de las piezas no encaja (un prefijo mal
 * leido, un destino mal mapeado, un convertidor de JSON que no se registra), el
 * mensaje simplemente no llega y el test lo ve.
 *
 * Los tres casos son justo la politica documentada en StompAuthChannelInterceptor:
 *
 *   - Con token: el SEND se difunde y se guarda, y el alias sale del token.
 *   - Sin token: leer (suscribirse) esta permitido.
 *   - Sin token: escribir se rechaza y no deja rastro.
 *
 * El contexto arranca con el mismo gate que EsquemaYMigracionesTest
 * (RADIOSTACK_DB_TESTS): estos tests piden PostgreSQL y un secreto JWT, y en el
 * CI los aporta el runner. Comparten el gate a proposito para que las dos
 * historias de base de datos entren o salgan juntas del recuento de tests.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@EnabledIfEnvironmentVariable(
        named = "RADIOSTACK_DB_TESTS",
        matches = "true",
        disabledReason = "necesita PostgreSQL; el CI lo levanta como servicio del runner")
class ChatStompEndToEndTest {

    @LocalServerPort
    private int puerto;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private JdbcTemplate jdbc;

    @Autowired
    private ChatService chatService;

    /** Contenidos creados por este test, para borrarlos al terminar. */
    private final List<String> creados = new ArrayList<>();

    @AfterEach
    void limpiarMensajes() {
        // El SEND se procesa en el hilo del servidor: el @Transactional del test
        // no alcanza a esa escritura, asi que la limpieza es explicita.
        for (String contenido : creados) {
            jdbc.update("delete from chat_message where contenido = ?", contenido);
        }
    }

    @Test
    void el_mensaje_enviado_con_token_se_guarda_y_se_difunde_con_el_alias_del_token() throws Exception {
        String contenido = "Mensaje e2e " + UUID.randomUUID();
        creados.add(contenido);
        Long emisionId = idDeUnaEmision();

        CountDownLatch llego = new CountDownLatch(1);
        AtomicReference<ChatMessageDTO> recibido = new AtomicReference<>();

        StompSession sesion = conectar(cabecerasDe("lucia@radiostack.com"));
        try {
            assertTrue(sesion.isConnected(), "la sesion no quedo conectada con el token");

            sesion.subscribe(topicoDe(emisionId), new StompFrameHandler() {
                @Override
                public Type getPayloadType(StompHeaders cabeceras) {
                    return ChatMessageDTO.class;
                }

                @Override
                public void handleFrame(StompHeaders cabeceras, Object payload) {
                    recibido.set((ChatMessageDTO) payload);
                    llego.countDown();
                }
            });

            // El canal entrante del broker los procesa con varios hilos, asi que
            // ni la misma conexion garantiza orden entre la suscripcion y el
            // envio, y el broker simple de Spring no emite RECEIPT. La espera
            // corta le da margen para registrar la suscripcion antes de difundir.
            Thread.sleep(300);

            sesion.send("/app/emisiones/%d/chat.send".formatted(emisionId),
                    Map.of("contenido", contenido));

            assertTrue(llego.await(10, TimeUnit.SECONDS),
                    "el topico " + topicoDe(emisionId) + " no recibio el mensaje");

            ChatMessageDTO dto = recibido.get();
            assertNotNull(dto, "no llego ningun mensaje al topico");
            assertEquals(contenido, dto.getContenido());
            assertEquals("lucia@radiostack.com", dto.getAlias(),
                    "el alias debe salir del token, no del cuerpo del mensaje");
            assertEquals(emisionId, dto.getEmisionId());

            boolean guardado = chatService.obtenerMensajesPorEmision(emisionId).stream()
                    .anyMatch(m -> contenido.equals(m.getContenido()));
            assertTrue(guardado, "el mensaje no quedo en el historial de la emision");
        } finally {
            desconectar(sesion);
        }
    }

    @Test
    void leer_el_chat_sin_token_esta_permitido() throws Exception {
        String contenido = "Mensaje e2e leido en publico " + UUID.randomUUID();
        creados.add(contenido);
        Long emisionId = idDeUnaEmision();

        CountDownLatch llego = new CountDownLatch(1);
        AtomicReference<ChatMessageDTO> recibido = new AtomicReference<>();

        StompSession lector = conectar(null);
        StompSession autor = conectar(cabecerasDe("lucia@radiostack.com"));
        try {
            assertTrue(lector.isConnected(),
                    "conectarse sin token deberia estar permitido para leer");

            lector.subscribe(topicoDe(emisionId), new StompFrameHandler() {
                @Override
                public Type getPayloadType(StompHeaders cabeceras) {
                    return ChatMessageDTO.class;
                }

                @Override
                public void handleFrame(StompHeaders cabeceras, Object payload) {
                    recibido.set((ChatMessageDTO) payload);
                    llego.countDown();
                }
            });

            // A diferencia del SEND, la suscripcion no devuelve ninguna
            // confirmacion (el broker simple de Spring no emite RECEIPT), y el
            // orden entre dos conexiones distintas no esta garantizado por el
            // protocolo. La espera corta le da al servidor margen para registrar
            // la suscripcion antes de que el mensaje del autor se difunda.
            Thread.sleep(300);

            autor.send("/app/emisiones/%d/chat.send".formatted(emisionId),
                    Map.of("contenido", contenido));

            assertTrue(llego.await(10, TimeUnit.SECONDS),
                    "el lector anonimo no recibio el mensaje difundido");
            assertNotNull(recibido.get());
            assertEquals(contenido, recibido.get().getContenido());
            assertEquals("lucia@radiostack.com", recibido.get().getAlias());
        } finally {
            desconectar(lector);
            desconectar(autor);
        }
    }

    @Test
    void enviar_sin_token_se_rechaza_y_no_guarda_nada() throws Exception {
        String contenido = "Mensaje e2e sin token " + UUID.randomUUID();
        creados.add(contenido);
        Long emisionId = idDeUnaEmision();

        RegistroDeErrores registro = new RegistroDeErrores();
        StompSession sesion = conectar(null, registro);
        try {
            assertTrue(sesion.isConnected(), "conectarse sin token deberia estar permitido");

            sesion.send("/app/emisiones/%d/chat.send".formatted(emisionId),
                    Map.of("contenido", contenido));

            // El servidor responde con un ERROR de STOMP (o cierra la conexion) y,
            // sobre todo, no procesa el mensaje. Esperar al rechazo garantiza que
            // el SEND llego al servidor antes de mirar el historial.
            registro.rechazo.await(10, TimeUnit.SECONDS);

            boolean guardado = chatService.obtenerMensajesPorEmision(emisionId).stream()
                    .anyMatch(m -> contenido.equals(m.getContenido()));
            assertFalse(guardado, "un SEND sin token no debe dejar nada en el historial");
        } finally {
            desconectar(sesion);
        }
    }

    /**
     * Registra la primera senal de rechazo del servidor. El ERROR de STOMP
     * llega por handleFrame, la excepcion de conversion por handleException y
     * el cierre de la conexion por handleTransportError; cualquiera de las tres
     * basta para saber que la trama no prospero.
     */
    private static final class RegistroDeErrores extends StompSessionHandlerAdapter {

        private final CountDownLatch rechazo = new CountDownLatch(1);

        @Override
        public Type getPayloadType(StompHeaders cabeceras) {
            return String.class;
        }

        @Override
        public void handleFrame(StompHeaders cabeceras, Object payload) {
            rechazo.countDown();
        }

        @Override
        public void handleException(StompSession sesion, StompCommand comando,
                                    StompHeaders cabeceras, byte[] payload, Throwable excepcion) {
            rechazo.countDown();
        }

        @Override
        public void handleTransportError(StompSession sesion, Throwable excepcion) {
            rechazo.countDown();
        }
    }

    private StompSession conectar(StompHeaders cabeceras) throws Exception {
        return conectar(cabeceras, new StompSessionHandlerAdapter() {
        });
    }

    /** Unico planificador para todos los clientes del test: negocia heartbeats. */
    private static final ThreadPoolTaskScheduler PLANIFICADOR = crearPlanificador();

    private static ThreadPoolTaskScheduler crearPlanificador() {
        ThreadPoolTaskScheduler planificador = new ThreadPoolTaskScheduler();
        planificador.setPoolSize(1);
        planificador.initialize();
        return planificador;
    }

    private StompSession conectar(StompHeaders cabeceras, StompSessionHandler manejador) throws Exception {
        WebSocketStompClient cliente = new WebSocketStompClient(new StandardWebSocketClient());

        // Sin JavaTimeModule, el convertidor no sabe leer el timestamp del
        // mensaje y la trama MESSAGE se cae al convertirla. El DTO que manda el
        // servidor lleva java.time.LocalDateTime.
        ObjectMapper mapeador = Jackson2ObjectMapperBuilder.json()
                .modules(new JavaTimeModule())
                .build();
        MappingJackson2MessageConverter convertidor = new MappingJackson2MessageConverter();
        convertidor.setObjectMapper(mapeador);
        cliente.setMessageConverter(convertidor);

        // Sin planificador no hay heartbeats: con el, la negociacion es completa.
        cliente.setTaskScheduler(PLANIFICADOR);

        URI url = URI.create("ws://localhost:%d/ws/stomp".formatted(puerto));
        if (cabeceras == null) {
            return cliente.connectAsync(url, (WebSocketHttpHeaders) null,
                    (StompHeaders) null, manejador).get(10, TimeUnit.SECONDS);
        }
        return cliente.connectAsync(url, (WebSocketHttpHeaders) null, cabeceras, manejador)
                .get(10, TimeUnit.SECONDS);
    }

    private StompHeaders cabecerasDe(String email) {
        Usuario usuario = new Usuario();
        usuario.setId(2L);
        usuario.setEmail(email);
        usuario.setRol(RolUsuario.LOCUTOR);

        StompHeaders cabeceras = new StompHeaders();
        cabeceras.add("Authorization", "Bearer " + jwtService.emitir(usuario));
        return cabeceras;
    }

    private static String topicoDe(Long emisionId) {
        return "/topic/emisiones/%d/chat".formatted(emisionId);
    }

    private Long idDeUnaEmision() {
        return jdbc.queryForObject("select id from emision order by id limit 1", Long.class);
    }

    private static void desconectar(StompSession sesion) {
        try {
            sesion.disconnect();
        } catch (RuntimeException ignorado) {
            // El servidor ya habia cerrado la conexion al rechazar la trama.
        }
    }
}