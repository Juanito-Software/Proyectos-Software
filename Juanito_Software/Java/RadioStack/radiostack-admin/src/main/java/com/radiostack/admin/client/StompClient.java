package com.radiostack.admin.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.function.Consumer;

/**
 * Cliente STOMP mínimo sobre WebSocket para conectar al broker de la API
 * (endpoint /ws/stomp). Envía CONNECT, SUBSCRIBE y SEND; parsea MESSAGE.
 */
public class StompClient extends WebSocketClient {

    private static final byte STOMP_FRAME_END = 0;
    private static final ObjectMapper JSON = new ObjectMapper();

    private final StringBuilder buffer = new StringBuilder();
    private Consumer<ChatMessage> onMessage;
    private Runnable onConnected;
    private Runnable onDisconnected;
    private volatile boolean stompConnected;

    public StompClient(String wsUri) {
        super(URI.create(wsUri));
    }

    public static StompClient create(String baseHttpUrl) {
        String ws = baseHttpUrl.replace("http://", "ws://").replace("https://", "wss://");
        return new StompClient(ws + "/ws/stomp");
    }

    public void setOnMessage(Consumer<ChatMessage> onMessage) {
        this.onMessage = onMessage;
    }

    public void setOnConnected(Runnable onConnected) {
        this.onConnected = onConnected;
    }

    public void setOnDisconnected(Runnable onDisconnected) {
        this.onDisconnected = onDisconnected;
    }

    @Override
    public void onOpen(ServerHandshake handshake) {
        sendStompFrame("CONNECT", "accept-version:1.2\nhost:localhost", null);
    }

    @Override
    public void onMessage(String message) {
        buffer.append(message);
        int end = buffer.indexOf(String.valueOf((char) STOMP_FRAME_END));
        while (end >= 0) {
            String frame = buffer.substring(0, end);
            buffer.delete(0, end + 1);
            handleFrame(frame);
            end = buffer.indexOf(String.valueOf((char) STOMP_FRAME_END));
        }
    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
        stompConnected = false;
        if (onDisconnected != null) runOnFx(onDisconnected);
    }

    @Override
    public void onError(Exception ex) {
        if (onDisconnected != null) runOnFx(onDisconnected);
    }

    private void handleFrame(String frame) {
        if (frame.isBlank()) return;
        int firstLineEnd = frame.indexOf('\n');
        if (firstLineEnd <= 0) return;
        String command = frame.substring(0, firstLineEnd).trim();
        String rest = frame.substring(firstLineEnd + 1);
        if ("CONNECTED".equals(command)) {
            stompConnected = true;
            if (onConnected != null) runOnFx(onConnected);
            return;
        }
        if ("MESSAGE".equals(command)) {
            int bodyStart = rest.indexOf("\n\n");
            String body = bodyStart >= 0 ? rest.substring(bodyStart + 2).trim() : "";
            if (onMessage != null && !body.isEmpty()) {
                try {
                    JsonNode node = JSON.readTree(body);
                    ChatMessage msg = new ChatMessage();
                    msg.id = node.has("id") ? node.get("id").asLong() : null;
                    msg.emisionId = node.has("emisionId") ? node.get("emisionId").asLong() : null;
                    msg.alias = node.has("alias") ? node.get("alias").asText() : "";
                    msg.contenido = node.has("contenido") ? node.get("contenido").asText() : "";
                    if (node.has("timestamp") && !node.get("timestamp").isNull()) {
                        JsonNode ts = node.get("timestamp");
                        msg.timestamp = ts.isTextual() ? ts.asText() : ts.toString();
                    } else {
                        msg.timestamp = "";
                    }
                    runOnFx(() -> onMessage.accept(msg));
                } catch (Exception ignored) {
                }
            }
        }
    }

    private void runOnFx(Runnable r) {
        try {
            javafx.application.Platform.runLater(r);
        } catch (Exception e) {
            r.run();
        }
    }

    public boolean isStompConnected() {
        return stompConnected && isOpen();
    }

    public void subscribe(long emisionId) {
        String dest = "/topic/emisiones/" + emisionId + "/chat";
        sendStompFrame("SUBSCRIBE", "id:sub-" + emisionId + "\ndestination:" + dest, null);
    }

    public void send(long emisionId, String alias, String contenido) {
        String dest = "/app/emisiones/" + emisionId + "/chat.send";
        String body = "{\"alias\":\"" + escapeJson(alias) + "\",\"contenido\":\"" + escapeJson(contenido) + "\"}";
        sendStompFrame("SEND", "destination:" + dest + "\ncontent-type:application/json\ncontent-length:" + body.length(), body);
    }

    private static String escapeJson(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
    }

    private void sendStompFrame(String command, String headers, String body) {
        if (!isOpen()) return;
        StringBuilder sb = new StringBuilder();
        sb.append(command).append('\n').append(headers).append("\n\n");
        if (body != null) sb.append(body);
        sb.append((char) STOMP_FRAME_END);
        send(sb.toString());
    }

    public void disconnectStomp() {
        stompConnected = false;
        close();
    }

    public static class ChatMessage {
        public Long id;
        public Long emisionId;
        public String alias;
        public String contenido;
        public String timestamp;
    }
}
