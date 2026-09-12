package com.radiostack.api.controller;

import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.core.domain.ChatMessage;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.service.ChatService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * La otra puerta del chat: la REST.
 *
 * ChatWebSocketController ya tenia sus tests y su alias salia del token. Este
 * controlador escribe en el MISMO ChatService, sobre la MISMA emision, y hasta
 * hoy tomaba el alias del cuerpo de la peticion. Cualquier usuario con cuenta
 * valida podia mandar {"alias": "locutor@radiostack.local", "contenido": "..."}
 * y el mensaje quedaba firmado con el email de otro; los oyentes lo recibian
 * por el mismo /topic, indistinguible de uno legitimo.
 *
 * Estos tests fijan que las dos puertas se comportan igual. No comprueban la
 * configuracion —eso lo hace SecurityConfigTest, que si levanta el filtro— sino
 * el efecto: con que argumentos se llama al servicio, y cuando no se le llama.
 */
@ExtendWith(MockitoExtension.class)
class ChatControllerTest {

    @Mock
    private ChatService chatService;

    private ChatController controlador() {
        return new ChatController(chatService);
    }

    private static UsuarioAutenticado usuario(String email) {
        return new UsuarioAutenticado(7L, email, "LOCUTOR");
    }

    private static ChatMessage mensajeGuardado(String alias, String contenido) {
        Emision emision = new Emision();
        emision.setId(42L);
        ChatMessage m = new ChatMessage();
        m.setId(1L);
        m.setEmision(emision);
        m.setAlias(alias);
        m.setContenido(contenido);
        m.setTimestamp(LocalDateTime.of(2026, 9, 12, 2, 30));
        return m;
    }

    @Test
    void el_alias_sale_del_token_y_no_del_cuerpo() {
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("otro@radiostack.local", "hola"));

        controlador().enviar(42L,
                Map.of("alias", "EL-JEFE", "contenido", "hola"),
                usuario("otro@radiostack.local"));

        // El alias del cuerpo se ignora por completo.
        verify(chatService).enviarMensaje(42L, "otro@radiostack.local", "hola");
    }

    @Test
    void suplantar_a_otro_usuario_escribiendo_su_email_en_el_cuerpo_ya_no_funciona() {
        // Este es literalmente el ataque: un usuario con cuenta firma como el
        // locutor de la emision. Antes del arreglo, el mensaje se guardaba con
        // el alias del cuerpo y ningun oyente podia notar la diferencia.
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("otro@radiostack.local", "Se cancela el programa"));

        controlador().enviar(42L,
                Map.of("alias", "locutor@radiostack.local", "contenido", "Se cancela el programa"),
                usuario("otro@radiostack.local"));

        verify(chatService).enviarMensaje(42L, "otro@radiostack.local", "Se cancela el programa");
        // Y en ningun caso con el email de la victima.
        verify(chatService, never()).enviarMensaje(anyLong(), eq("locutor@radiostack.local"), anyString());
    }

    @Test
    void sin_identidad_no_se_publica_nada() {
        ResponseStatusException error = assertThrows(ResponseStatusException.class,
                () -> controlador().enviar(42L, Map.of("contenido", "hola"), null));

        // 401 y no 403: no es que no tengas permiso, es que no has dicho quien
        // eres. Mismo criterio que el punto de entrada de SecurityConfig.
        assertEquals(HttpStatus.UNAUTHORIZED, error.getStatusCode());
        verify(chatService, never()).enviarMensaje(anyLong(), any(), any());
    }

    @Test
    void devuelve_el_mensaje_guardado_convertido_a_dto() {
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("otro@radiostack.local", "hola"));

        ChatMessageDTO dto = controlador()
                .enviar(42L, Map.of("contenido", "hola"), usuario("otro@radiostack.local"));

        // Se devuelve el mensaje tal y como quedo guardado, no el que se pidio:
        // el alias es el del token y el sello de tiempo lo puso el servidor.
        assertEquals(1L, dto.getId().longValue());
        assertEquals(42L, dto.getEmisionId().longValue());
        assertEquals("otro@radiostack.local", dto.getAlias());
        assertEquals("hola", dto.getContenido());
    }

    @Test
    void un_cuerpo_sin_contenido_manda_cadena_vacia_y_no_revienta() {
        // Comportamiento heredado, y se deja escrito para que el dia que se
        // decida rechazar los mensajes vacios sea un cambio deliberado y no una
        // sorpresa. Lo importante aqui es que no lanza NullPointerException.
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("otro@radiostack.local", ""));

        controlador().enviar(42L, Map.of(), usuario("otro@radiostack.local"));

        verify(chatService).enviarMensaje(42L, "otro@radiostack.local", "");
    }

    @Test
    void la_emision_es_la_de_la_ruta_aunque_el_cuerpo_traiga_otra() {
        // El cuerpo es un Map<String, String> abierto: acepta cualquier clave.
        // Que una de ellas se llame «emisionId» no debe cambiar nada.
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("otro@radiostack.local", "hola"));

        controlador().enviar(42L,
                Map.of("emisionId", "1", "contenido", "hola"),
                usuario("otro@radiostack.local"));

        verify(chatService).enviarMensaje(42L, "otro@radiostack.local", "hola");
    }

    @Test
    void listar_devuelve_los_mensajes_convertidos_a_dto() {
        when(chatService.obtenerMensajesPorEmision(42L)).thenReturn(List.of(
                mensajeGuardado("ana@radiostack.local", "primero"),
                mensajeGuardado("bea@radiostack.local", "segundo")));

        List<ChatMessageDTO> dtos = controlador().listar(42L);

        assertEquals(2, dtos.size());
        assertEquals("ana@radiostack.local", dtos.get(0).getAlias());
        assertEquals("segundo", dtos.get(1).getContenido());
    }

    @Test
    void listar_no_pide_identidad_porque_leer_el_chat_es_publico() {
        // No hay parametro de usuario en `listar`, y esa ausencia es la regla:
        // si algun dia se añade, leer dejaria de ser publico sin que nadie lo
        // decidiera. El test falla en cuanto la firma cambie.
        when(chatService.obtenerMensajesPorEmision(42L)).thenReturn(List.of());

        assertTrue(controlador().listar(42L).isEmpty());
        verify(chatService).obtenerMensajesPorEmision(42L);
    }
}
