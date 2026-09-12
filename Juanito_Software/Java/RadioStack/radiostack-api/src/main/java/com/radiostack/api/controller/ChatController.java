package com.radiostack.api.controller;

import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.core.service.ChatService;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/emisiones/{emisionId}/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    /**
     * Historial del chat de una emision.
     *
     * Publico, igual que el resto de los GET de /api/v1: lo que se dice en el
     * chat de un programa en directo es parte del programa. Leerlo no requiere
     * identidad; escribir, si.
     */
    @GetMapping
    public List<ChatMessageDTO> listar(@PathVariable Long emisionId) {
        return chatService.obtenerMensajesPorEmision(emisionId).stream()
                .map(DtoMapper::toChatMessageDTO)
                .toList();
    }

    /**
     * Publica un mensaje en el chat de una emision.
     *
     * El alias sale del token, no del cuerpo. Antes se leia asi:
     *
     *     String alias = body.getOrDefault("alias", "Anónimo");
     *
     * y eso permitia a cualquier usuario con cuenta valida firmar un mensaje
     * con el nombre de otro: bastaba con enviar {"alias": "locutor@...",
     * "contenido": "..."}. El mensaje se guardaba y se difundia por el mismo
     * /topic que los legitimos, de modo que ningun oyente podia distinguirlos.
     *
     * La suplantacion ya se habia cerrado en ChatWebSocketController, que toma
     * el alias del token verificado en el CONNECT de STOMP. Pero las dos clases
     * escriben en el MISMO ChatService y en la MISMA emision, asi que tapar una
     * sola puerta no servia de nada: quedaba esta abierta, y ademas era la mas
     * comoda de usar, porque un POST no necesita ni cliente de WebSocket.
     *
     * La leccion, y por eso queda escrita aqui: cuando un recurso tiene dos
     * entradas, la politica de identidad se arregla en las dos a la vez o no se
     * arregla.
     *
     * El 401 explicito no deberia llegar a ocurrir: SecurityConfig ya exige
     * token para todo lo que no sea GET. Se mantiene por la misma razon que el
     * equivalente del controlador de WebSocket: depender en silencio de que
     * otra clase vigile es como se cuelan los fallos de seguridad, y si algun
     * dia alguien anade esta ruta a las publicas, el fallo sale por aqui en vez
     * de convertirse en mensajes sin autor.
     */
    @PostMapping
    public ChatMessageDTO enviar(@PathVariable Long emisionId,
                                 @RequestBody Map<String, String> body,
                                 @AuthenticationPrincipal UsuarioAutenticado usuario) {

        if (usuario == null) {
            throw new ResponseStatusException(
                    HttpStatus.UNAUTHORIZED, "Se requiere autenticacion para escribir en el chat.");
        }

        String contenido = body.getOrDefault("contenido", "");
        return DtoMapper.toChatMessageDTO(
                chatService.enviarMensaje(emisionId, usuario.email(), contenido));
    }
}
