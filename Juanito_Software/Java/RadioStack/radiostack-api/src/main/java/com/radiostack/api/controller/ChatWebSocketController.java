package com.radiostack.api.controller;

import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.service.ChatService;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;

import java.util.Map;

@Controller
public class ChatWebSocketController {

    private final ChatService chatService;

    public ChatWebSocketController(ChatService chatService) {
        this.chatService = chatService;
    }

    @MessageMapping("/emisiones/{emisionId}/chat.send")
    @SendTo("/topic/emisiones/{emisionId}/chat")
    public ChatMessageDTO enviar(@DestinationVariable Long emisionId, Map<String, String> payload) {
        String alias = payload.getOrDefault("alias", "Anónimo");
        String contenido = payload.getOrDefault("contenido", "");
        var msg = chatService.enviarMensaje(emisionId, alias, contenido);
        return DtoMapper.toChatMessageDTO(msg);
    }
}
