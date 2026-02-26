package com.radiostack.api.service;

import com.radiostack.core.domain.ChatMessage;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.ChatMessageRepository;
import com.radiostack.core.port.EmisionRepository;
import com.radiostack.core.service.ChatService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class ChatServiceImpl implements ChatService {

    private final ChatMessageRepository chatMessageRepository;
    private final EmisionRepository emisionRepository;

    public ChatServiceImpl(ChatMessageRepository chatMessageRepository,
                           EmisionRepository emisionRepository) {
        this.chatMessageRepository = chatMessageRepository;
        this.emisionRepository = emisionRepository;
    }

    @Override
    @Transactional
    public ChatMessage enviarMensaje(Long emisionId, String alias, String contenido) {
        Emision emision = emisionRepository.findById(emisionId)
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada: " + emisionId));
        ChatMessage msg = new ChatMessage();
        msg.setEmision(emision);
        msg.setAlias(alias);
        msg.setContenido(contenido);
        msg.setTimestamp(LocalDateTime.now());
        return chatMessageRepository.save(msg);
    }

    @Override
    @Transactional(readOnly = true)
    public List<ChatMessage> obtenerMensajesPorEmision(Long emisionId) {
        Emision emision = emisionRepository.findById(emisionId)
                .orElseThrow(() -> new IllegalArgumentException("Emisión no encontrada: " + emisionId));
        return chatMessageRepository.findByEmision(emision);
    }
}
