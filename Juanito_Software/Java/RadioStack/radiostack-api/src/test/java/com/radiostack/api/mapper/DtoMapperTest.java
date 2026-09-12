package com.radiostack.api.mapper;

import com.radiostack.api.dto.ChatMessageDTO;
import com.radiostack.api.dto.ComentarioDTO;
import com.radiostack.api.dto.EmisionDTO;
import com.radiostack.api.dto.LocutorDTO;
import com.radiostack.api.dto.ProgramaDTO;
import com.radiostack.api.dto.UsuarioDTO;
import com.radiostack.core.domain.ChatMessage;
import com.radiostack.core.domain.Comentario;
import com.radiostack.core.domain.DiaSemana;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.domain.EstadoComentario;
import com.radiostack.core.domain.EstadoEmision;
import com.radiostack.core.domain.Locutor;
import com.radiostack.core.domain.Programa;
import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.time.LocalDateTime;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * La frontera entre el dominio y lo que sale por la API.
 *
 * Dos cosas que se prueban aqui y en ningun otro sitio: que ningun DTO arrastre
 * el hash de la contraseña, y que convertir una entidad a medio rellenar —sin
 * programa, sin usuario, sin emision— no reviente. Eso ultimo pasa de verdad:
 * JPA devuelve relaciones nulas cuando la fila no las tiene, y un NullPointer
 * aqui se traduce en un 500 al pintar una pantalla entera.
 */
class DtoMapperTest {

    private static Usuario usuario() {
        Usuario u = new Usuario();
        u.setId(7L);
        u.setNombre("Juanito DJ");
        u.setEmail("locutor@radiostack.local");
        u.setPasswordHash("$2a$10$HASH-QUE-NO-DEBE-SALIR");
        u.setRol(RolUsuario.LOCUTOR);
        u.setActivo(true);
        return u;
    }

    @Test
    void el_dto_de_usuario_no_tiene_sitio_donde_guardar_la_contrasena() throws Exception {
        // Se comprueba sobre la clase, no sobre una instancia: asi el test salta si
        // alguien añade el campo, aunque no lo rellene todavia.
        for (Field campo : UsuarioDTO.class.getDeclaredFields()) {
            String nombre = campo.getName().toLowerCase();
            assertFalse(nombre.contains("password") || nombre.contains("hash"),
                    "UsuarioDTO no debe tener el campo " + campo.getName());
        }
    }

    @Test
    void convierte_el_usuario_con_el_rol_como_texto() {
        UsuarioDTO dto = DtoMapper.toUsuarioDTO(usuario());

        assertEquals(7L, dto.getId().longValue());
        assertEquals("Juanito DJ", dto.getNombre());
        assertEquals("locutor@radiostack.local", dto.getEmail());
        assertEquals("LOCUTOR", dto.getRol());
        assertTrue(dto.isActivo());
    }

    @Test
    void un_usuario_sin_rol_no_revienta() {
        Usuario sinRol = usuario();
        sinRol.setRol(null);

        assertNull(DtoMapper.toUsuarioDTO(sinRol).getRol());
    }

    @Test
    void convierte_el_programa_con_los_ids_de_sus_locutores() {
        Locutor locutor = new Locutor(3L, "DJ Cayon", usuario());
        Programa p = new Programa();
        p.setId(1L);
        p.setNombre("Madrugada");
        p.setCategoria("musica");
        p.setActivo(true);
        p.setLocutores(Set.of(locutor));

        ProgramaDTO dto = DtoMapper.toProgramaDTO(p);

        assertEquals("Madrugada", dto.getNombre());
        assertEquals(Set.of(3L), dto.getLocutorIds());
    }

    @Test
    void convierte_la_emision_con_el_nombre_del_programa_y_los_enums_como_texto() {
        Programa p = new Programa();
        p.setId(1L);
        p.setNombre("Madrugada");
        Emision e = new Emision();
        e.setId(42L);
        e.setPrograma(p);
        e.setDiaSemana(DiaSemana.SABADO);
        e.setHoraInicio(LocalDateTime.of(2026, 9, 19, 23, 0));
        e.setHoraFin(LocalDateTime.of(2026, 9, 20, 1, 0));
        e.setEstado(EstadoEmision.PROGRAMADO);

        EmisionDTO dto = DtoMapper.toEmisionDTO(e);

        assertEquals(1L, dto.getProgramaId().longValue());
        assertEquals("Madrugada", dto.getProgramaNombre());
        assertEquals("SABADO", dto.getDiaSemana());
        assertEquals("PROGRAMADO", dto.getEstado());
        assertEquals(LocalDateTime.of(2026, 9, 19, 23, 0), dto.getHoraInicio());
    }

    @Test
    void una_emision_sin_programa_ni_estado_no_revienta() {
        Emision e = new Emision();
        e.setId(42L);

        EmisionDTO dto = DtoMapper.toEmisionDTO(e);

        assertNull(dto.getProgramaId());
        assertNull(dto.getProgramaNombre());
        assertNull(dto.getDiaSemana());
        assertNull(dto.getEstado());
    }

    @Test
    void convierte_el_locutor_con_los_datos_de_su_usuario() {
        LocutorDTO dto = DtoMapper.toLocutorDTO(new Locutor(3L, "DJ Cayon", usuario()));

        assertEquals("DJ Cayon", dto.getNombreArtistico());
        assertEquals(7L, dto.getUsuarioId().longValue());
        assertEquals("locutor@radiostack.local", dto.getUsuarioEmail());
    }

    @Test
    void un_locutor_sin_usuario_no_revienta() {
        Locutor sinUsuario = new Locutor();
        sinUsuario.setId(3L);
        sinUsuario.setNombreArtistico("DJ Cayon");

        LocutorDTO dto = DtoMapper.toLocutorDTO(sinUsuario);

        assertNull(dto.getUsuarioId());
        assertNull(dto.getUsuarioEmail());
    }

    @Test
    void convierte_el_comentario_con_su_estado_de_moderacion() {
        Emision e = new Emision();
        e.setId(42L);
        Comentario c = new Comentario();
        c.setId(5L);
        c.setEmision(e);
        c.setAutor("oyente");
        c.setMensaje("gran programa");
        c.setTimestamp(LocalDateTime.of(2026, 9, 11, 23, 30));
        c.setEstado(EstadoComentario.MODERADO);

        ComentarioDTO dto = DtoMapper.toComentarioDTO(c);

        assertEquals(42L, dto.getEmisionId().longValue());
        assertEquals("oyente", dto.getAutor());
        assertEquals("MODERADO", dto.getEstado());
    }

    @Test
    void convierte_el_mensaje_de_chat_con_el_id_de_su_emision() {
        Emision e = new Emision();
        e.setId(42L);
        ChatMessage m = new ChatMessage(1L, e, "Juanito DJ", "buenas noches",
                LocalDateTime.of(2026, 9, 11, 23, 30));

        ChatMessageDTO dto = DtoMapper.toChatMessageDTO(m);

        assertEquals(1L, dto.getId().longValue());
        assertEquals(42L, dto.getEmisionId().longValue());
        assertEquals("Juanito DJ", dto.getAlias());
        assertEquals("buenas noches", dto.getContenido());
    }

    @Test
    void un_mensaje_de_chat_sin_emision_no_revienta() {
        ChatMessage m = new ChatMessage();
        m.setId(1L);
        m.setContenido("huerfano");

        assertNull(DtoMapper.toChatMessageDTO(m).getEmisionId());
    }

    @Test
    void convertir_null_devuelve_null_en_todos_los_mapeos() {
        // Los controladores mapean con `.map(DtoMapper::...)` sobre resultados que
        // pueden venir vacios; devolver null es mas barato que comprobarlo en cada
        // llamada, pero solo si se cumple en todos.
        assertNull(DtoMapper.toUsuarioDTO(null));
        assertNull(DtoMapper.toProgramaDTO(null));
        assertNull(DtoMapper.toEmisionDTO(null));
        assertNull(DtoMapper.toLocutorDTO(null));
        assertNull(DtoMapper.toComentarioDTO(null));
        assertNull(DtoMapper.toChatMessageDTO(null));
    }
}
