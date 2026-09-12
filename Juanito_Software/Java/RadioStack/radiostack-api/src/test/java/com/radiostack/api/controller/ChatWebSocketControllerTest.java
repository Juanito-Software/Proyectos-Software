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
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Publicar en el chat por WebSocket.
 *
 * La razon de ser de este controlador: el alias ya no se toma del cuerpo del
 * mensaje. Cuando venia en el payload, cualquiera podia firmar con el nombre que
 * quisiera y hacerse pasar por otro locutor. Ahora sale del token verificado en
 * el CONNECT, que es la unica fuente de identidad que el servidor puede
 * comprobar.
 */
@ExtendWith(MockitoExtension.class)
class ChatWebSocketControllerTest {

    @Mock
    private ChatService chatService;

    private ChatWebSocketController controlador() {
        return new ChatWebSocketController(chatService);
    }

    private static Authentication sesionDe(String email) {
        return new UsernamePasswordAuthenticationToken(
                new UsuarioAutenticado(7L, email, "LOCUTOR"), null, List.of());
    }

    private static ChatMessage mensajeGuardado(String alias, String contenido) {
        Emision emision = new Emision();
        emision.setId(42L);
        ChatMessage m = new ChatMessage();
        m.setId(1L);
        m.setEmision(emision);
        m.setAlias(alias);
        m.setContenido(contenido);
        m.setTimestamp(LocalDateTime.of(2026, 9, 11, 23, 30));
        return m;
    }

    @Test
    void el_alias_sale_del_token_y_no_del_payload() {
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("locutor@radiostack.local", "hola"));

        controlador().enviar(42L, Map.of("alias", "EL-JEFE", "contenido", "hola"), sesionDe("locutor@radiostack.local"));

        // El alias del payload («EL-JEFE») se ignora por completo.
        verify(chatService).enviarMensaje(42L, "locutor@radiostack.local", "hola");
    }

    @Test
    void devuelve_el_mensaje_guardado_convertido_a_dto() {
        when(chatService.enviarMensaje(anyLong(), anyString(), anyString()))
                .thenReturn(mensajeGuardado("locutor@radiostack.local", "hola"));

        ChatMessageDTO dto = controlador()
                .enviar(42L, Map.of("contenido", "hola"), sesionDe("locutor@radiostack.local"));

        // Lo que se difunde a /topic es este DTO: id de emision, alias y contenido,
        // nada del usuario que lo escribio mas alla del alias.
        assertEquals(1L, dto.getId().longValue());
        assertEquals(42L, dto.getEmisionId().longValue());
        assertEquals("locutor@radiostack.local", dto.getAlias());
        assertEquals("hola", dto.getContenido());
    }

    @Test
    void sin_identidad_no_se_publica_nada() {
        // StompAuthChannelInterceptor ya rechaza los SEND sin usuario, asi que aqui
        // no deberia llegar ninguno. La comprobacion se mantiene porque depender de
        // otra clase sin decirlo es como se cuelan los fallos de seguridad.
        assertThrows(IllegalStateException.class,
                () -> controlador().enviar(42L, Map.of("contenido", "hola"), null));

        verify(chatService, never()).enviarMensaje(anyLong(), anyString(), anyString());
    }

    @Test
    void con_un_principal_que_no_es_un_usuario_autenticado_tampoco() {
        Authentication raro = new UsernamePasswordAuthenticationToken("anonymous", null, List.of());

        assertThrows(IllegalStateException.class,
                () -> controlador().enviar(42L, Map.of("contenido", "hola"), raro));

        verify(chatService, never()).enviarMensaje(anyLong(), any(), any());
    }
}
