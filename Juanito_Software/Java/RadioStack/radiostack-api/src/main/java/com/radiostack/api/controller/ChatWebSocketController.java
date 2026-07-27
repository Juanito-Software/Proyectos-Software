package com.radiostack.api.controller;

import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.core.service.ChatService;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Controller
public class ChatWebSocketController {

    private final ChatService chatService;

    public ChatWebSocketController(ChatService chatService) {
        this.chatService = chatService;
    }

    /**
     * Publica un mensaje en el chat de una emision.
     *
     * El alias ya no se toma del cuerpo del mensaje. Antes venia en el payload,
     * asi que cualquiera podia firmar con el nombre que quisiera y hacerse
     * pasar por otro. Ahora sale del token verificado en la trama CONNECT, que
     * es la unica fuente de identidad que el servidor puede comprobar.
     *
     * Cuando este metodo se ejecuta, StompAuthChannelInterceptor ya ha
     * rechazado cualquier SEND sin usuario, de modo que 'auth' no puede ser
     * nulo aqui. La comprobacion se mantiene por si esa politica cambiase:
     * dependencias implicitas entre dos clases distintas es como se cuelan los
     * fallos de seguridad.
     */
    @MessageMapping("/emisiones/{emisionId}/chat.send")
    @SendTo("/topic/emisiones/{emisionId}/chat")
    public ChatMessageDTO enviar(@DestinationVariable Long emisionId,
                                 Map<String, String> payload,
                                 Authentication auth) {

        if (auth == null || !(auth.getPrincipal() instanceof UsuarioAutenticado usuario)) {
            throw new IllegalStateException("Mensaje sin identidad autenticada.");
        }

        String contenido = payload.getOrDefault("contenido", "");
        var msg = chatService.enviarMensaje(emisionId, usuario.email(), contenido);
        return DtoMapper.toChatMessageDTO(msg);
    }
}
