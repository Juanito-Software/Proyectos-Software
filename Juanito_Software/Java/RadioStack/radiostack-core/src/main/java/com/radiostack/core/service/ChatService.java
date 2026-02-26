package com.radiostack.core.service;

import com.radiostack.core.domain.ChatMessage;

import java.util.List;

public interface ChatService {

    ChatMessage enviarMensaje(Long emisionId, String alias, String contenido);

    List<ChatMessage> obtenerMensajesPorEmision(Long emisionId);
}

