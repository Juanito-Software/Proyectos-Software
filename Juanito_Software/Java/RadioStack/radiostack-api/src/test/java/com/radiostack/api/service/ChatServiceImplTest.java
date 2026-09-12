package com.radiostack.api.service;

import com.radiostack.core.domain.ChatMessage;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.port.ChatMessageRepository;
import com.radiostack.core.port.EmisionRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Mensajes del chat.
 *
 * Lo que importa aqui es que un mensaje nunca quede colgando de una emision que
 * no existe, y que el sello de tiempo lo ponga el servidor: si viniera del
 * cliente, cualquiera podria datar sus mensajes donde quisiera y desordenar el
 * chat de los demas.
 */
@ExtendWith(MockitoExtension.class)
class ChatServiceImplTest {

    @Mock
    private ChatMessageRepository chatMessageRepository;
    @Mock
    private EmisionRepository emisionRepository;

    private ChatServiceImpl servicio() {
        return new ChatServiceImpl(chatMessageRepository, emisionRepository);
    }

    private static Emision emision() {
        Emision e = new Emision();
        e.setId(42L);
        return e;
    }

    @Test
    void enviar_a_una_emision_que_no_existe_no_guarda_nada() {
        when(emisionRepository.findById(99L)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> servicio().enviarMensaje(99L, "alias", "hola"));

        assertTrue(error.getMessage().contains("99"));
        verify(chatMessageRepository, never()).save(any());
    }

    @Test
    void enviar_guarda_el_mensaje_colgado_de_su_emision() {
        Emision emision = emision();
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision));
        when(chatMessageRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        servicio().enviarMensaje(42L, "Juanito DJ", "buenas noches");

        ArgumentCaptor<ChatMessage> guardado = ArgumentCaptor.forClass(ChatMessage.class);
        verify(chatMessageRepository).save(guardado.capture());
        assertSame(emision, guardado.getValue().getEmision());
        assertEquals("Juanito DJ", guardado.getValue().getAlias());
        assertEquals("buenas noches", guardado.getValue().getContenido());
    }

    @Test
    void el_sello_de_tiempo_lo_pone_el_servidor() {
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision()));
        when(chatMessageRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        LocalDateTime antes = LocalDateTime.now().minusSeconds(1);
        servicio().enviarMensaje(42L, "alias", "hola");

        ArgumentCaptor<ChatMessage> guardado = ArgumentCaptor.forClass(ChatMessage.class);
        verify(chatMessageRepository).save(guardado.capture());
        LocalDateTime sello = guardado.getValue().getTimestamp();
        assertNotNull(sello);
        assertTrue(sello.isAfter(antes), "el sello de tiempo no es de ahora: " + sello);
        assertTrue(Duration.between(sello, LocalDateTime.now()).toMinutes() < 1);
    }

    @Test
    void devuelve_el_mensaje_tal_como_lo_ha_guardado_el_repositorio() {
        // El id lo asigna la base de datos, asi que quien llama necesita el objeto
        // devuelto por el repositorio, no el que se construyo aqui.
        ChatMessage persistido = new ChatMessage();
        persistido.setId(500L);
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision()));
        when(chatMessageRepository.save(any())).thenReturn(persistido);

        assertSame(persistido, servicio().enviarMensaje(42L, "alias", "hola"));
    }

    @Test
    void listar_los_mensajes_de_una_emision_que_no_existe_es_un_error_y_no_una_lista_vacia() {
        // Devolver una lista vacia haria pasar por «emision sin mensajes» lo que en
        // realidad es un id equivocado.
        when(emisionRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> servicio().obtenerMensajesPorEmision(99L));
        verify(chatMessageRepository, never()).findByEmision(any());
    }

    @Test
    void listar_pide_los_mensajes_de_esa_emision_concreta() {
        Emision emision = emision();
        ChatMessage uno = new ChatMessage();
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision));
        when(chatMessageRepository.findByEmision(emision)).thenReturn(List.of(uno));

        List<ChatMessage> mensajes = servicio().obtenerMensajesPorEmision(42L);

        assertEquals(1, mensajes.size());
        assertSame(uno, mensajes.get(0));
    }
}
