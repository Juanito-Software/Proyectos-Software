package com.radiostack.core.port;

import com.radiostack.core.domain.ChatMessage;
import com.radiostack.core.domain.Emision;

import java.util.List;

public interface ChatMessageRepository {

    ChatMessage save(ChatMessage message);

    List<ChatMessage> findByEmision(Emision emision);
}

