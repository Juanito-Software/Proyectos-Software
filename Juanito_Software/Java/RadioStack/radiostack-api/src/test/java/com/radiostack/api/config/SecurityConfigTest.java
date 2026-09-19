package com.radiostack.api.config;

import com.radiostack.api.controller.AuthController;
import com.radiostack.api.controller.ChatController;
import com.radiostack.api.controller.ParrillaController;
import com.radiostack.api.security.JwtAuthenticationFilter;
import com.radiostack.api.security.JwtService;
import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import com.radiostack.core.service.ChatService;
import com.radiostack.core.service.ParrillaService;
import com.radiostack.core.service.UsuarioService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringBootConfiguration;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Las reglas de acceso de SecurityConfig, comprobadas a traves de la cadena de
 * filtros de verdad.
 *
 * Es el PRIMER test de RadioStack que levanta un contexto de Spring, y es
 * deliberado: las reglas de esta clase no existen como metodo al que llamar,
 * existen como comportamiento de la cadena de filtros. Un test que construyera
 * SecurityConfig con `new` no probaria nada, porque lo que se quiere fijar es
 * que una peticion concreta entra o se queda fuera.
 *
 * Por que este test declara su propio @SpringBootConfiguration (la clase
 * ContextoWebDePrueba, al final del fichero) en vez de usar
 * RadiostackApiApplication:
 *
 *   El conocimiento JPA de RadioStack es una configuracion normal de Spring,
 *   @EntityScan y @EnableJpaRepositories en com.radiostack.persistence.config.
 *   No es delito en si: la rodaja podria excluirla con un filtro de
 *   @ComponentScan. El problema es que la aplicacion no es solo JpaConfig. El
 *   escaneo del paquete base de @SpringBootApplication barre com.radiostack de
 *   arriba a abajo: ademas de la configuracion de persistencia encontraria
 *   DataInitializer y el resto de beans que exigen repositorios y servicios
 *   reales, y una rodaja web no tiene BD que ofrecerles. El contexto ni siquiera
 *   llegaria a arrancar.
 *
 *   Con una configuracion propia y las clases traidas una a una con @Import, no
 *   hay escaneo de componentes y el contexto contiene exactamente lo que se
 *   quiere probar: SecurityConfig y JwtAuthenticationFilter, que son las clases
*   de PRODUCCION, mas los controladores con los que se atraviesan las
 *   reglas. Nada de JPA, nada de PostgreSQL, nada de Flyway.
 *
 *   Quien quiera una rodaja montada sobre la aplicacion real ya puede hacerlo
 *   sin parches: excluir JpaConfig y los beans dependientes con
 *   @ComponentScan.Filter y el contexto completa; antes de mover esas
 *   anotaciones, puestas como estaban en la clase raiz, @WebMvcTest no podia
 *   apagarlas ni con un filtro.
 *
 * JwtService NO se sustituye por un doble: se construye uno real con una clave
 * de prueba. Asi los tokens de estos tests recorren el mismo camino que los de
 * produccion —firma, caducidad, claims— y no se prueba un decorado.
 *
 * Como se distingue quien devuelve un 401. Hay dos fuentes posibles y significan
 * cosas distintas:
 *
 *   - El punto de entrada de SecurityConfig usa `sendError`, que ademas del
 *     codigo deja un mensaje de error en la respuesta. Ese 401 significa «la
 *     cadena de filtros te ha parado».
 *   - Un controlador que devuelve `ResponseEntity.status(401)` no deja mensaje.
 *     Ese 401 significa «la peticion ha llegado hasta el codigo».
 *
 * Mirar `getErrorMessage()` es lo que permite comprobar cual de los dos ha sido,
 * que es justo lo que hace falta para saber si una ruta esta protegida por la
 * configuracion o solo por el controlador.
 */
@WebMvcTest(
        // application.yml lee `radiostack.jwt.secret` de la variable de entorno
        // RADIOSTACK_JWT_SECRET, y no tiene valor por defecto a proposito. Estas
        // dos propiedades estan aqui solo para que ese marcador nunca se quede
        // sin resolver si algun dia alguien lo inyecta en esta rodaja; NO son la
        // clave con la que se firman los tokens de estos tests, que es SECRETO.
        properties = {
                "radiostack.jwt.secret=c2VjcmV0by1kZS1wcnVlYmEtcXVlLW5vLXNlLXVzYS1lbi1uaW5ndW4tc2l0aW8=",
                "radiostack.jwt.expiration-seconds=3600"
        })
@Import({
        // Las dos clases de produccion que se estan probando.
        SecurityConfig.class,
        JwtAuthenticationFilter.class,
        // Y los controladores a traves de los cuales se atraviesan sus reglas.
        ChatController.class,
        AuthController.class,
        ParrillaController.class
})
class SecurityConfigTest {

    /**
     * Clave de firma solo para estos tests. 48 bytes, que supera los 32 que
     * exige HMAC-SHA256; con menos, JwtService se niega a arrancar.
     */
    private static final String SECRETO = Base64.getEncoder()
            .encodeToString("clave-de-prueba-de-48-bytes-para-firmar-con-hmac!".getBytes(StandardCharsets.UTF_8));

    @TestConfiguration
    static class ServicioDeTokens {
        @Bean
        JwtService jwtService() {
            return new JwtService(SECRETO, 3600);
        }
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @MockBean
    private ChatService chatService;

    @MockBean
    private ParrillaService parrillaService;

    @MockBean
    private UsuarioService usuarioService;

    private static final String CHAT = "/api/v1/emisiones/42/chat";
    private static final String CUERPO = "{\"contenido\":\"hola\"}";

    private static Usuario locutor() {
        Usuario u = new Usuario();
        u.setId(7L);
        u.setNombre("Locutor");
        u.setEmail("locutor@radiostack.local");
        u.setRol(RolUsuario.LOCUTOR);
        u.setActivo(true);
        return u;
    }

    private String tokenValido() {
        return jwtService.emitir(locutor());
    }

    // -----------------------------------------------------------------------
    // Escribir exige identidad
    // -----------------------------------------------------------------------

    @Test
    void un_post_sin_token_recibe_401_de_la_cadena_de_filtros() throws Exception {
        MvcResult res = mockMvc.perform(post(CHAT).contentType(MediaType.APPLICATION_JSON).content(CUERPO))
                .andExpect(status().isUnauthorized())
                .andReturn();

        // 401 y no 403. Sin el punto de entrada de SecurityConfig, Spring
        // Security responderia 403 a una peticion sin credenciales, que le dice
        // al cliente «no tienes permiso» cuando lo cierto es «no te has
        // identificado»: dos problemas distintos con soluciones distintas.
        assertEquals("Se requiere autenticacion", res.getResponse().getErrorMessage());

        // Y sobre todo: el controlador no ha llegado a ejecutarse.
        verify(chatService, never()).enviarMensaje(anyLong(), anyString(), anyString());
    }

    @Test
    void un_post_con_un_token_que_no_vale_tambien_recibe_401() throws Exception {
        MvcResult res = mockMvc.perform(post(CHAT)
                        .header("Authorization", "Bearer esto-no-es-un-token")
                        .contentType(MediaType.APPLICATION_JSON).content(CUERPO))
                .andExpect(status().isUnauthorized())
                .andReturn();

        assertEquals("Se requiere autenticacion", res.getResponse().getErrorMessage());
        verify(chatService, never()).enviarMensaje(anyLong(), anyString(), anyString());
    }

    @Test
    void un_token_firmado_con_otra_clave_no_autentica() throws Exception {
        // Un token con la forma correcta y los claims correctos, pero firmado
        // por otro. Si la verificacion de la firma se desactivara, este seria el
        // test que lo delataria: todo lo demas del token es valido.
        String otraClave = Base64.getEncoder()
                .encodeToString("otra-clave-distinta-de-48-bytes-para-firmar-aqui!".getBytes(StandardCharsets.UTF_8));
        String impostor = new JwtService(otraClave, 3600).emitir(locutor());

        mockMvc.perform(post(CHAT)
                        .header("Authorization", "Bearer " + impostor)
                        .contentType(MediaType.APPLICATION_JSON).content(CUERPO))
                .andExpect(status().isUnauthorized());

        verify(chatService, never()).enviarMensaje(anyLong(), anyString(), anyString());
    }

    @Test
    void cualquier_escritura_exige_token_aunque_la_ruta_no_exista() throws Exception {
        // La regla es `anyRequest().authenticated()`, no una lista de rutas.
        // Si alguien la cambiara por una enumeracion, una ruta nueva quedaria
        // abierta sin que nadie lo decidiera.
        //
        // Se comprueba con una ruta inexistente a proposito: si la peticion
        // pasara el filtro, la respuesta seria 404 (no hay controlador). Que sea
        // 401 demuestra que se ha parado ANTES de buscar controlador.
        mockMvc.perform(put("/api/v1/ruta-que-no-existe").contentType(MediaType.APPLICATION_JSON).content("{}"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void con_un_token_valido_se_escribe_y_el_alias_es_el_del_token() throws Exception {
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(new com.radiostack.core.domain.ChatMessage());

        mockMvc.perform(post(CHAT)
                        .header("Authorization", "Bearer " + tokenValido())
                        .contentType(MediaType.APPLICATION_JSON).content(CUERPO))
                .andExpect(status().isOk());

        // Dos cosas a la vez: el filtro ha puesto la identidad en el contexto
        // (si no, el controlador habria lanzado 401), y el alias que llega al
        // servicio es el del token.
        verify(chatService).enviarMensaje(42L, "locutor@radiostack.local", "hola");
    }

    @Test
    void escribir_no_pide_token_csrf_porque_la_api_no_usa_cookies() throws Exception {
        // El test anterior ya lo demuestra de paso, pero merece quedar escrito
        // solo: CSRF esta desactivado a proposito, no por descuido. Un ataque
        // CSRF necesita que el navegador adjunte credenciales por su cuenta, y
        // esta API no emite ninguna cookie; se autentica con una cabecera que el
        // navegador no añade solo.
        //
        // Si algun dia se añade sesion o cookie, este test seguira en verde y
        // por eso el comentario importa: lo que hay que revisar entonces es la
        // decision, no el test.
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(new com.radiostack.core.domain.ChatMessage());

        mockMvc.perform(post(CHAT)
                        .header("Authorization", "Bearer " + tokenValido())
                        .contentType(MediaType.APPLICATION_JSON).content(CUERPO))
                .andExpect(status().isOk());
    }

    // -----------------------------------------------------------------------
    // Leer es publico
    // -----------------------------------------------------------------------

    @Test
    void leer_el_chat_no_pide_token() throws Exception {
        when(chatService.obtenerMensajesPorEmision(42L)).thenReturn(List.of());

        mockMvc.perform(get(CHAT)).andExpect(status().isOk());

        verify(chatService).obtenerMensajesPorEmision(42L);
    }

    @Test
    void la_parrilla_se_puede_leer_sin_token() throws Exception {
        // Este es el destinatario pensado de la regla `GET /api/v1/** ->
        // permitAll`: la parrilla y los programas son informacion para los
        // oyentes, no datos de usuario. A diferencia del chat, aqui hay un
        // controlador que devuelve el contenido que se quiere publicar, y este
        // test fija que atraviesa la cadena de filtros sin identidad y llega al
        // controlador. Si algun dia se restringe la regla, el primer GET de
        // catalogo que lo delatara seria este.
        when(parrillaService.obtenerParrilla(any(), any())).thenReturn(List.of());

        mockMvc.perform(get("/api/v1/parrilla?from=2026-09-19&to=2026-09-20"))
                .andExpect(status().isOk());

        verify(parrillaService).obtenerParrilla(any(), any());
    }

    @Test
    void las_rutas_publicas_de_fuera_de_api_v1_tampoco_piden_token() throws Exception {
        // Ninguna de estas tres tiene controlador en esta rodaja, asi que la
        // respuesta esperada es 404. Y ese 404 es precisamente la prueba: si la
        // regla `permitAll` no estuviera, serian 401, porque la cadena de
        // filtros para antes de llegar a buscar controlador.
        //
        // - /ws/**: el handshake del WebSocket no puede llevar cabecera
        //   Authorization, asi que se autentica una trama despues, en el CONNECT
        //   de STOMP.
        // - la documentacion y el health, para poder consultarlos sin cuenta.
        mockMvc.perform(get("/ws/chat")).andExpect(status().isNotFound());
        mockMvc.perform(get("/v3/api-docs")).andExpect(status().isNotFound());
        mockMvc.perform(get("/actuator/health")).andExpect(status().isNotFound());
    }

    // -----------------------------------------------------------------------
    // Login
    // -----------------------------------------------------------------------

    @Test
    void el_login_es_accesible_sin_haber_iniciado_sesion() throws Exception {
        Usuario u = locutor();
        u.setPasswordHash(passwordEncoder.encode("secreta"));
        when(usuarioService.buscarPorEmail("locutor@radiostack.local")).thenReturn(Optional.of(u));

        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"locutor@radiostack.local\",\"password\":\"secreta\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isNotEmpty());

        // Sin el permitAll explicito, esta ruta caeria en `anyRequest()` por ser
        // un POST y nadie podria iniciar sesion nunca: haria falta un token para
        // pedir un token.
    }

    @Test
    void el_login_con_la_contrasena_equivocada_no_emite_token() throws Exception {
        Usuario u = locutor();
        u.setPasswordHash(passwordEncoder.encode("secreta"));
        when(usuarioService.buscarPorEmail("locutor@radiostack.local")).thenReturn(Optional.of(u));

        MvcResult res = mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"locutor@radiostack.local\",\"password\":\"la-que-no-es\"}"))
                .andExpect(status().isUnauthorized())
                .andReturn();

        // Este 401 lo devuelve el controlador, no la cadena de filtros: la ruta
        // es publica y la peticion ha llegado hasta el codigo. Sin mensaje de
        // error en la respuesta es como se distingue.
        assertNull(res.getResponse().getErrorMessage());
    }

    // -----------------------------------------------------------------------
    // El caso incomodo: /api/v1/auth/me
    // -----------------------------------------------------------------------

    @Test
    void me_sin_token_lo_rechaza_el_controlador_y_no_la_configuracion() throws Exception {
        MvcResult res = mockMvc.perform(get("/api/v1/auth/me"))
                .andExpect(status().isUnauthorized())
                .andReturn();

        // Sin mensaje de error: la peticion ha atravesado la cadena de filtros y
        // ha llegado al controlador, que ha visto el principal a null.
        //
        // El motivo es la regla `GET /api/v1/** -> permitAll`, pensada para la
        // parrilla y los programas, que son informacion para los oyentes. Pero
        // alcanza a TODOS los GET de la API, incluido este. Aqui no se escapa
        // nada porque AuthController se defiende solo; el riesgo es el GET que
        // alguien añada mañana bajo /api/v1 dando por hecho que esta protegido.
        //
        // Este test no aprueba esa regla: la deja documentada y con una alarma.
        // Si se decide restringirla, el que fallara sera este y no un incidente.
        assertNull(res.getResponse().getErrorMessage());
        verify(usuarioService, never()).obtenerPorId(anyLong());
    }

    @Test
    void me_con_token_valido_devuelve_el_usuario_del_token() throws Exception {
        when(usuarioService.obtenerPorId(7L)).thenReturn(Optional.of(locutor()));

        mockMvc.perform(get("/api/v1/auth/me").header("Authorization", "Bearer " + tokenValido()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.usuario.email").value("locutor@radiostack.local"));

        // Comprueba el eslabon que ningun test unitario puede comprobar: que el
        // filtro deja el UsuarioAutenticado donde @AuthenticationPrincipal lo
        // busca, y que el id que se consulta es el del `sub` del token.
        verify(usuarioService).obtenerPorId(7L);
    }

    @Test
    void el_token_no_viaja_en_la_respuesta_de_me() throws Exception {
        when(usuarioService.obtenerPorId(7L)).thenReturn(Optional.of(locutor()));

        MvcResult res = mockMvc.perform(get("/api/v1/auth/me").header("Authorization", "Bearer " + tokenValido()))
                .andExpect(status().isOk())
                .andReturn();

        // /me describe al usuario; no renueva la sesion. Devolver el token aqui
        // seria repetirlo sin necesidad en un sitio mas donde puede acabar
        // registrado o cacheado.
        String cuerpo = res.getResponse().getContentAsString();
        assertNotNull(cuerpo);
        assertEquals(-1, cuerpo.indexOf("\"token\":\""), "la respuesta de /me trae un token: " + cuerpo);
    }

    @Test
    void una_cuenta_desactivada_no_pasa_aunque_su_token_siga_siendo_valido() throws Exception {
        // Los JWT no se pueden revocar: el token de alguien a quien se le acaba
        // de dar de baja sigue verificando bien hasta que caduque. La unica
        // defensa es comprobarlo contra la base de datos en cada peticion.
        Usuario baja = locutor();
        baja.setActivo(false);
        when(usuarioService.obtenerPorId(7L)).thenReturn(Optional.of(baja));

        mockMvc.perform(get("/api/v1/auth/me").header("Authorization", "Bearer " + tokenValido()))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void el_filtro_ignora_una_cabecera_authorization_mal_formada_sin_romper_la_peticion() throws Exception {
        // Sin el prefijo «Bearer ». El filtro no debe lanzar ni cortar: deja el
        // contexto vacio y sigue, y es SecurityConfig quien decide. Como leer es
        // publico, la peticion tiene que salir adelante igualmente.
        when(chatService.obtenerMensajesPorEmision(42L)).thenReturn(List.of());

        mockMvc.perform(get(CHAT).header("Authorization", tokenValido()))
                .andExpect(status().isOk());

        verify(chatService).obtenerMensajesPorEmision(42L);
    }
}

/**
 * Configuracion raiz de la rodaja web de SecurityConfigTest.
 *
 * @WebMvcTest busca hacia arriba, desde el paquete del test, la primera clase
 * anotada con @SpringBootConfiguration. Al existir esta, se para aqui y no llega
 * a RadiostackApiApplication, que es lo que se quiere evitar: el escaneo del
 * paquete base de esa clase barre com.radiostack entero y encontraria, ademas de
 * la configuracion JPA del modulo de persistencia, los beans que dependen de
 * repositorios y servicios reales; en una rodaja web no hay base de datos con la
 * que construirlos. (El conocimiento JPA en si ya es un bean excluible, pero la
 * aplicacion no es solo ese bean.)
 *
 * No lleva @ComponentScan a proposito: en este contexto no se escanea nada. Todo
 * lo que hay dentro entra por el @Import del test o por @MockBean, de modo que
 * el contenido del contexto es exactamente el que se lee en las anotaciones y no
 * depende de que clase este anotada con que en el resto del modulo.
 *
 * Es package-private y vive en el mismo fichero que el test porque solo existe
 * para el: si aparece en otro sitio, es que alguien la ha movido sin querer.
 */
@SpringBootConfiguration
@EnableAutoConfiguration
class ContextoWebDePrueba {
}
