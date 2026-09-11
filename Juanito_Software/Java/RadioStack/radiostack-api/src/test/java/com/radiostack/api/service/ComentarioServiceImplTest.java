package com.radiostack.api.service;

import com.radiostack.core.domain.Comentario;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.domain.EstadoComentario;
import com.radiostack.core.port.ComentarioRepository;
import com.radiostack.core.port.EmisionRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Comentarios de los oyentes y su moderacion.
 *
 * El estado inicial es el que decide si un comentario se ve en cuanto se
 * publica. Aqui es `VISIBLE`, es decir, la radio publica sin revisar y modera
 * despues; dejarlo escrito es lo que convierte ese comportamiento en una
 * decision y no en un descuido.
 */
@ExtendWith(MockitoExtension.class)
class ComentarioServiceImplTest {

    @Mock
    private ComentarioRepository comentarioRepository;
    @Mock
    private EmisionRepository emisionRepository;

    private ComentarioServiceImpl servicio() {
        return new ComentarioServiceImpl(comentarioRepository, emisionRepository);
    }

    private static Emision emision() {
        Emision e = new Emision();
        e.setId(42L);
        return e;
    }

    @Test
    void publicar_en_una_emision_que_no_existe_no_guarda_nada() {
        when(emisionRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> servicio().publicarComentario(99L, "oyente", "hola"));
        verify(comentarioRepository, never()).save(any());
    }

    @Test
    void publicar_guarda_autor_mensaje_y_emision() {
        Emision emision = emision();
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision));
        when(comentarioRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        servicio().publicarComentario(42L, "oyente", "gran programa");

        ArgumentCaptor<Comentario> guardado = ArgumentCaptor.forClass(Comentario.class);
        verify(comentarioRepository).save(guardado.capture());
        assertSame(emision, guardado.getValue().getEmision());
        assertEquals("oyente", guardado.getValue().getAutor());
        assertEquals("gran programa", guardado.getValue().getMensaje());
        assertNotNull(guardado.getValue().getTimestamp());
    }

    @Test
    void un_comentario_nuevo_nace_visible() {
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision()));
        when(comentarioRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        servicio().publicarComentario(42L, "oyente", "hola");

        ArgumentCaptor<Comentario> guardado = ArgumentCaptor.forClass(Comentario.class);
        verify(comentarioRepository).save(guardado.capture());
        assertEquals(EstadoComentario.VISIBLE, guardado.getValue().getEstado());
    }

    @Test
    void moderar_un_comentario_que_no_existe_es_un_error() {
        when(comentarioRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class,
                () -> servicio().cambiarEstadoComentario(99L, EstadoComentario.BLOQUEADO));
        verify(comentarioRepository, never()).save(any());
    }

    @Test
    void moderar_guarda_el_estado_nuevo_sin_tocar_el_resto() {
        Comentario existente = new Comentario();
        existente.setId(5L);
        existente.setMensaje("mensaje original");
        existente.setEstado(EstadoComentario.VISIBLE);
        when(comentarioRepository.findById(5L)).thenReturn(Optional.of(existente));
        when(comentarioRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        servicio().cambiarEstadoComentario(5L, EstadoComentario.BLOQUEADO);

        ArgumentCaptor<Comentario> guardado = ArgumentCaptor.forClass(Comentario.class);
        verify(comentarioRepository).save(guardado.capture());
        assertEquals(EstadoComentario.BLOQUEADO, guardado.getValue().getEstado());
        assertEquals("mensaje original", guardado.getValue().getMensaje());
    }

    @Test
    void listar_los_comentarios_de_una_emision_que_no_existe_es_un_error() {
        when(emisionRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> servicio().listarComentariosPorEmision(99L));
        verify(comentarioRepository, never()).findByEmision(any());
    }

    @Test
    void listar_pide_los_comentarios_de_esa_emision() {
        Emision emision = emision();
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision));
        when(comentarioRepository.findByEmision(emision)).thenReturn(List.of(new Comentario()));

        assertEquals(1, servicio().listarComentariosPorEmision(42L).size());
    }

    @Test
    void listar_devuelve_tambien_los_moderados_y_bloqueados() {
        // El servicio no filtra por estado: quien decida que se pinta es la capa de
        // arriba. Queda escrito porque un comentario BLOQUEADO que llegue al
        // navegador es un fallo de moderacion, y asi se sabe donde mirar.
        Emision emision = emision();
        Comentario visible = new Comentario();
        visible.setEstado(EstadoComentario.VISIBLE);
        Comentario bloqueado = new Comentario();
        bloqueado.setEstado(EstadoComentario.BLOQUEADO);
        when(emisionRepository.findById(42L)).thenReturn(Optional.of(emision));
        when(comentarioRepository.findByEmision(emision)).thenReturn(List.of(visible, bloqueado));

        assertEquals(2, servicio().listarComentariosPorEmision(42L).size());
    }
}
