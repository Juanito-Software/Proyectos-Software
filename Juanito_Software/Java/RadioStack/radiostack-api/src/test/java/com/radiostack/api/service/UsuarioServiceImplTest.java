package com.radiostack.api.service;

import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import com.radiostack.core.port.UsuarioRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Altas y bajas de usuarios.
 *
 * Dos reglas con consecuencias: un email no puede registrarse dos veces —es la
 * clave con la que se inicia sesion—, y el alta ignora el id que llegue, para
 * que nadie pueda sobrescribir la cuenta de otro enviando su identificador.
 */
@ExtendWith(MockitoExtension.class)
class UsuarioServiceImplTest {

    @Mock
    private UsuarioRepository usuarioRepository;

    private UsuarioServiceImpl servicio() {
        return new UsuarioServiceImpl(usuarioRepository);
    }

    private static Usuario usuario(Long id, boolean activo) {
        Usuario u = new Usuario();
        u.setId(id);
        u.setNombre("Juanito DJ");
        u.setEmail("locutor@radiostack.local");
        u.setPasswordHash("$2a$10$HASH");
        u.setRol(RolUsuario.LOCUTOR);
        u.setActivo(activo);
        return u;
    }

    @Test
    void registrar_un_email_que_ya_existe_no_guarda_nada() {
        when(usuarioRepository.findByEmail("locutor@radiostack.local")).thenReturn(Optional.of(usuario(1L, true)));

        assertThrows(IllegalArgumentException.class, () -> servicio().registrarUsuario(usuario(null, true)));

        verify(usuarioRepository, never()).save(any());
    }

    @Test
    void registrar_ignora_el_id_que_llegue_en_el_objeto() {
        // Con el id puesto, `save` seria un UPDATE: un alta podria sobrescribir la
        // cuenta de otro usuario.
        when(usuarioRepository.findByEmail(any())).thenReturn(Optional.empty());
        when(usuarioRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

        servicio().registrarUsuario(usuario(99L, true));

        ArgumentCaptor<Usuario> guardado = ArgumentCaptor.forClass(Usuario.class);
        verify(usuarioRepository).save(guardado.capture());
        assertNull(guardado.getValue().getId());
    }

    @Test
    void registrar_devuelve_el_usuario_que_ha_guardado_el_repositorio() {
        Usuario persistido = usuario(10L, true);
        when(usuarioRepository.findByEmail(any())).thenReturn(Optional.empty());
        when(usuarioRepository.save(any())).thenReturn(persistido);

        assertSame(persistido, servicio().registrarUsuario(usuario(null, true)));
    }

    @Test
    void desactivar_un_usuario_que_no_existe_es_un_error() {
        when(usuarioRepository.findById(99L)).thenReturn(Optional.empty());

        IllegalArgumentException error = assertThrows(IllegalArgumentException.class,
                () -> servicio().desactivarUsuario(99L));

        assertTrue(error.getMessage().contains("99"));
        verify(usuarioRepository, never()).save(any());
    }

    @Test
    void desactivar_guarda_la_cuenta_como_inactiva() {
        when(usuarioRepository.findById(7L)).thenReturn(Optional.of(usuario(7L, true)));

        servicio().desactivarUsuario(7L);

        ArgumentCaptor<Usuario> guardado = ArgumentCaptor.forClass(Usuario.class);
        verify(usuarioRepository).save(guardado.capture());
        assertFalse(guardado.getValue().isActivo());
    }

    @Test
    void activar_un_usuario_que_no_existe_es_un_error() {
        when(usuarioRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> servicio().activarUsuario(99L));
        verify(usuarioRepository, never()).save(any());
    }

    @Test
    void activar_guarda_la_cuenta_como_activa() {
        when(usuarioRepository.findById(7L)).thenReturn(Optional.of(usuario(7L, false)));

        servicio().activarUsuario(7L);

        ArgumentCaptor<Usuario> guardado = ArgumentCaptor.forClass(Usuario.class);
        verify(usuarioRepository).save(guardado.capture());
        assertTrue(guardado.getValue().isActivo());
    }

    @Test
    void buscar_por_email_delega_en_el_repositorio() {
        // Es el camino del login: si alguna vez se le añadiera un filtro aqui,
        // cambiaria quien puede iniciar sesion.
        Usuario u = usuario(7L, true);
        when(usuarioRepository.findByEmail("locutor@radiostack.local")).thenReturn(Optional.of(u));

        assertSame(u, servicio().buscarPorEmail("locutor@radiostack.local").orElseThrow());
    }

    @Test
    void obtener_por_id_delega_en_el_repositorio() {
        Usuario u = usuario(7L, true);
        when(usuarioRepository.findById(7L)).thenReturn(Optional.of(u));

        assertSame(u, servicio().obtenerPorId(7L).orElseThrow());
    }

    @Test
    void listar_devuelve_lo_que_hay_en_el_repositorio() {
        when(usuarioRepository.findAll()).thenReturn(List.of(usuario(1L, true), usuario(2L, false)));

        assertEquals(2, servicio().listarUsuarios().size());
    }
}
