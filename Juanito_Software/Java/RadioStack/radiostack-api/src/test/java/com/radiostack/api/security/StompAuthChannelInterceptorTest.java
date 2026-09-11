package com.radiostack.api.security;

import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;
import org.springframework.messaging.Message;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.security.Principal;
import java.util.Base64;
import java.util.Date;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Autenticacion del canal STOMP, que es donde se protege el chat.
 *
 * El filtro JWT de HTTP no llega hasta aqui: una conexion WebSocket se abre con
 * un unico handshake —que la API de los navegadores no permite acompañar de
 * cabeceras— y despues las tramas viajan por un canal ya establecido, al margen
 * del ciclo peticion-respuesta. De ahi que el handshake quede abierto en
 * SecurityConfig y el control se haga una trama mas tarde, en el CONNECT.
 *
 * El criterio es el mismo que en HTTP, para no tener dos politicas segun el
 * transporte: leer el chat es publico, escribir exige token.
 */
class StompAuthChannelInterceptorTest {

    private static final String SECRETO = Base64.getEncoder()
            .encodeToString("clave-de-prueba-de-48-bytes-para-firmar-con-hmac!".getBytes(StandardCharsets.UTF_8));

    private final JwtService jwtService = new JwtService(SECRETO, 3600);
    private final StompAuthChannelInterceptor interceptor = new StompAuthChannelInterceptor(jwtService);

    private static Usuario usuario() {
        Usuario u = new Usuario();
        u.setId(7L);
        u.setEmail("locutor@radiostack.local");
        u.setRol(RolUsuario.LOCUTOR);
        u.setActivo(true);
        return u;
    }

    /**
     * Crea la trama y se queda con el accesor, que es donde el interceptor deja
     * el usuario. Los headers se construyen desde el accesor para que
     * `MessageHeaderAccessor.getAccessor` lo recupere, igual que en produccion.
     */
    private record Trama(Message<byte[]> mensaje, StompHeaderAccessor accesor) {
    }

    private static Trama trama(StompCommand comando, String cabecera, Principal usuarioPrevio) {
        StompHeaderAccessor accesor = StompHeaderAccessor.create(comando);
        accesor.setLeaveMutable(true);
        if (cabecera != null) {
            accesor.setNativeHeader("Authorization", cabecera);
        }
        if (usuarioPrevio != null) {
            accesor.setUser(usuarioPrevio);
        }
        return new Trama(MessageBuilder.createMessage(new byte[0], accesor.getMessageHeaders()), accesor);
    }

    private static Principal sesionAutenticada() {
        return new UsernamePasswordAuthenticationToken(
                new UsuarioAutenticado(7L, "locutor@radiostack.local", "LOCUTOR"), null, List.of());
    }

    @Test
    void el_connect_con_token_valido_deja_al_usuario_en_la_sesion() {
        Trama t = trama(StompCommand.CONNECT, "Bearer " + jwtService.emitir(usuario()), null);

        interceptor.preSend(t.mensaje(), null);

        assertNotNull(t.accesor().getUser());
        UsuarioAutenticado autenticado = assertInstanceOf(
                UsuarioAutenticado.class,
                ((UsernamePasswordAuthenticationToken) t.accesor().getUser()).getPrincipal());
        assertEquals(7L, autenticado.id().longValue());
        assertEquals("locutor@radiostack.local", autenticado.email());
    }

    @Test
    void el_usuario_de_la_sesion_lleva_la_autoridad_con_prefijo_ROLE_() {
        Trama t = trama(StompCommand.CONNECT, "Bearer " + jwtService.emitir(usuario()), null);

        interceptor.preSend(t.mensaje(), null);

        var auth = (UsernamePasswordAuthenticationToken) t.accesor().getUser();
        assertTrue(auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_LOCUTOR")));
    }

    @Test
    void el_connect_sin_cabecera_deja_la_sesion_anonima() {
        // Un oyente sin cuenta tiene que poder leer el chat, igual que puede leer
        // la parrilla por HTTP.
        Trama t = trama(StompCommand.CONNECT, null, null);

        interceptor.preSend(t.mensaje(), null);

        assertNull(t.accesor().getUser());
    }

    @Test
    void el_connect_con_un_token_invalido_se_rechaza_en_vez_de_degradarse_a_anonimo() {
        // Si se aceptara como anonimo, quien tuviera el token caducado veria el chat
        // pero no podria escribir, sin saber por que. Mejor que el cliente se
        // entere de que su sesion ya no vale.
        Trama t = trama(StompCommand.CONNECT, "Bearer token-que-no-vale", null);

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> interceptor.preSend(t.mensaje(), null));
        assertTrue(error.getMessage().contains("Token invalido"));
        assertNull(t.accesor().getUser());
    }

    @Test
    void el_connect_con_la_cabecera_mal_formada_se_rechaza() {
        Trama t = trama(StompCommand.CONNECT, "Token abc", null);

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> interceptor.preSend(t.mensaje(), null));
        assertTrue(error.getMessage().contains("mal formada"));
    }

    @Test
    void el_connect_con_un_token_caducado_se_rechaza() {
        String caducado = new JwtService(SECRETO, -60).emitir(usuario());
        Trama t = trama(StompCommand.CONNECT, "Bearer " + caducado, null);

        assertThrows(IllegalArgumentException.class, () -> interceptor.preSend(t.mensaje(), null));
    }

    @Test
    void el_connect_con_un_token_firmado_pero_sin_email_ni_rol_se_rechaza() {
        // Mismo criterio que en HTTP: las dos puertas aceptan los mismos tokens. Si
        // esta pasara, el alias de los mensajes del chat —que sale del email— seria
        // «null» para todo el mundo.
        SecretKey clave = Keys.hmacShaKeyFor(Base64.getDecoder().decode(SECRETO));
        String sinClaims = Jwts.builder()
                .subject("7")
                .expiration(new Date(System.currentTimeMillis() + 60_000))
                .signWith(clave)
                .compact();
        Trama t = trama(StompCommand.CONNECT, "Bearer " + sinClaims, null);

        assertThrows(IllegalArgumentException.class, () -> interceptor.preSend(t.mensaje(), null));
        assertNull(t.accesor().getUser());
    }

    @Test
    void escribir_sin_identidad_se_rechaza() {
        // Es la regla que sostiene que el alias del chat no se pueda falsificar: sin
        // usuario en la sesion, la trama no llega al controlador.
        Trama t = trama(StompCommand.SEND, null, null);

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> interceptor.preSend(t.mensaje(), null));
        assertTrue(error.getMessage().contains("Se requiere autenticacion"));
    }

    @Test
    void escribir_con_identidad_pasa() {
        Trama t = trama(StompCommand.SEND, null, sesionAutenticada());

        Message<?> resultado = interceptor.preSend(t.mensaje(), null);

        assertSame(t.mensaje(), resultado);
    }

    @Test
    void suscribirse_sin_identidad_pasa() {
        // Leer es publico: un SUBSCRIBE anonimo a /topic no se toca.
        Trama t = trama(StompCommand.SUBSCRIBE, null, null);

        assertSame(t.mensaje(), interceptor.preSend(t.mensaje(), null));
    }

    @Test
    void desconectarse_sin_identidad_pasa() {
        // Solo CONNECT y SEND se inspeccionan. Un DISCONNECT anonimo —el de un
        // oyente que cierra la pagina— no debe convertirse en un error.
        Trama t = trama(StompCommand.DISCONNECT, null, null);

        assertSame(t.mensaje(), interceptor.preSend(t.mensaje(), null));
    }

    @Test
    void un_mensaje_que_no_es_stomp_pasa_sin_tocarlo() {
        Message<String> ajeno = MessageBuilder.withPayload("hola").build();

        assertSame(ajeno, interceptor.preSend(ajeno, null));
    }
}
