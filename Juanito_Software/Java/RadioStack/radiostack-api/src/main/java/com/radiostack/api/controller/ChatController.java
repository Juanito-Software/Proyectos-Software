package com.radiostack.api.controller;

import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.service.ChatService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/emisiones/{emisionId}/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @GetMapping
    public List<ChatMessageDTO> listar(@PathVariable Long emisionId) {
        return chatService.obtenerMensajesPorEmision(emisionId).stream()
                .map(DtoMapper::toChatMessageDTO)
                .toList();
    }

    @PostMapping
    public ChatMessageDTO enviar(@PathVariable Long emisionId, @RequestBody Map<String, String> body) {
        String alias = body.getOrDefault("alias", "Anónimo");
        String contenido = body.getOrDefault("contenido", "");
        return DtoMapper.toChatMessageDTO(chatService.enviarMensaje(emisionId, alias, contenido));
    }
}
