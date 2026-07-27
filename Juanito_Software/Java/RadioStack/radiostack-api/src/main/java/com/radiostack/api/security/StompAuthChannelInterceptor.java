package com.radiostack.api.security;

import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.messaging.support.ChannelInterceptor;
import org.springframework.messaging.support.MessageHeaderAccessor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * Autenticacion del canal STOMP.
 *
 * El filtro JWT de HTTP no sirve aqui. Una conexion WebSocket se abre con un
 * unico handshake y despues las tramas viajan por un canal ya establecido, al
 * margen del ciclo peticion-respuesta donde actuan los filtros de servlet. Y el
 * handshake tampoco lleva la cabecera Authorization, porque la API de WebSocket
 * de los navegadores no permite anadir cabeceras.
 *
 * La solucion habitual, y la que se aplica aqui, es autenticar en la trama
 * CONNECT de STOMP: es la primera que envia el cliente y admite cabeceras
 * propias. El usuario resultante queda asociado a la sesion y las tramas
 * posteriores lo heredan.
 *
 * El criterio de acceso es el mismo que en HTTP, para no tener dos politicas
 * distintas segun el transporte:
 *
 *   - Leer el chat (SUBSCRIBE a /topic) es publico, igual que los GET.
 *   - Escribir (SEND a /app) exige token valido, igual que POST y PUT.
 */
@Component
public class StompAuthChannelInterceptor implements ChannelInterceptor {

    private static final String CABECERA = "Authorization";
    private static final String PREFIJO = "Bearer ";

    private final JwtService jwtService;

    public StompAuthChannelInterceptor(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    @Override
    public Message<?> preSend(Message<?> message, MessageChannel channel) {
        StompHeaderAccessor accessor =
                MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);

        if (accessor == null || accessor.getCommand() == null) {
            return message;
        }

        if (StompCommand.CONNECT.equals(accessor.getCommand())) {
            autenticar(accessor);
        } else if (StompCommand.SEND.equals(accessor.getCommand())) {
            if (accessor.getUser() == null) {
                // Sin identidad no se escribe. Lanzar aqui aborta la trama y
                // el cliente recibe un ERROR de STOMP.
                throw new IllegalArgumentException(
                        "Se requiere autenticacion para enviar mensajes al chat.");
            }
        }

        return message;
    }

    /**
     * Lee el token de la trama CONNECT y, si es valido, asocia el usuario a la
     * sesion.
     *
     * Un token ausente se admite: deja la sesion anonima, que basta para leer.
     * Un token presente pero invalido se rechaza en lugar de degradarse a
     * anonimo, porque significa que algo va mal (caducado, manipulado) y es
     * preferible que el cliente se entere.
     */
    private void autenticar(StompHeaderAccessor accessor) {
        List<String> valores = accessor.getNativeHeader(CABECERA);
        if (valores == null || valores.isEmpty()) {
            return;
        }

        String cabecera = valores.get(0);
        if (cabecera == null || !cabecera.startsWith(PREFIJO)) {
            throw new IllegalArgumentException("Cabecera Authorization mal formada.");
        }

        String token = cabecera.substring(PREFIJO.length()).trim();
        var claims = jwtService.verificar(token)
                .orElseThrow(() -> new IllegalArgumentException("Token invalido o caducado."));

        UsuarioAutenticado usuario = new UsuarioAutenticado(
                Long.parseLong(claims.getSubject()),
                claims.get("email", String.class),
                claims.get("rol", String.class));

        accessor.setUser(new UsernamePasswordAuthenticationToken(
                usuario,
                null,
                List.of(new SimpleGrantedAuthority("ROLE_" + usuario.rol()))));
    }
}
