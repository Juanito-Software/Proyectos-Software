package com.radiostack.persistence.adapter;

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
import com.radiostack.persistence.entity.ChatMessageEntity;
import com.radiostack.persistence.entity.ComentarioEntity;
import com.radiostack.persistence.entity.EmisionEntity;
import com.radiostack.persistence.entity.LocutorEntity;
import com.radiostack.persistence.entity.ProgramaEntity;
import com.radiostack.persistence.entity.UsuarioEntity;
import com.radiostack.persistence.repository.jpa.ChatMessageJpaRepository;
import com.radiostack.persistence.repository.jpa.ComentarioJpaRepository;
import com.radiostack.persistence.repository.jpa.EmisionJpaRepository;
import com.radiostack.persistence.repository.jpa.LocutorJpaRepository;
import com.radiostack.persistence.repository.jpa.ProgramaJpaRepository;
import com.radiostack.persistence.repository.jpa.UsuarioJpaRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

/**
 * Los seis adaptadores que conectan los puertos del dominio con Spring Data.
 *
 * Son clases finas —mapear, delegar, mapear de vuelta— y esa delgadez es
 * precisamente lo que hace facil romperlas sin darse cuenta. Los dos errores que
 * estos tests vigilan son:
 *
 *   1. Devolver lo que se recibio en vez de lo que devolvio el repositorio. Es
 *      un cambio que parece equivalente y no lo es: al guardar algo nuevo, el id
 *      lo genera la base de datos, y quien devuelve el objeto de entrada
 *      devuelve un id nulo. El error aparece mucho despues, en quien esperaba
 *      poder usar ese id.
 *
 *   2. Convertir cuando no hay nada que convertir. Un `findById` que no encuentra
 *      nada tiene que devolver `Optional.empty()` sin pasar por el mapeador.
 *
 * Los repositorios JPA se sustituyen por dobles: aqui no hay PostgreSQL ni
 * contexto de Spring. Lo que se comprueba es el contrato entre el adaptador y su
 * repositorio, no que la consulta SQL sea correcta —eso solo lo puede decir una
 * base de datos de verdad, y es el hueco siguiente de la lista.
 */
@ExtendWith(MockitoExtension.class)
class AdaptadoresDePersistenciaTest {

    private static final LocalDateTime INICIO = LocalDateTime.of(2026, 9, 12, 20, 0);
    private static final LocalDateTime FIN = LocalDateTime.of(2026, 9, 12, 22, 0);

    @Mock private UsuarioJpaRepository usuarioJpa;
    @Mock private LocutorJpaRepository locutorJpa;
    @Mock private ProgramaJpaRepository programaJpa;
    @Mock private EmisionJpaRepository emisionJpa;
    @Mock private ComentarioJpaRepository comentarioJpa;
    @Mock private ChatMessageJpaRepository chatJpa;

    private static UsuarioEntity entidadUsuario(Long id, String email) {
        UsuarioEntity e = new UsuarioEntity();
        e.setId(id);
        e.setNombre("Ana");
        e.setEmail(email);
        e.setPasswordHash("hash");
        e.setRol(RolUsuario.LOCUTOR);
        e.setActivo(true);
        return e;
    }

    private static EmisionEntity entidadEmision(Long id) {
        EmisionEntity e = new EmisionEntity();
        e.setId(id);
        e.setDiaSemana(DiaSemana.JUEVES);
        e.setHoraInicio(INICIO);
        e.setHoraFin(FIN);
        e.setEstado(EstadoEmision.PROGRAMADO);
        return e;
    }

    private static Emision emisionDeDominio(Long id) {
        return new Emision(id, null, DiaSemana.JUEVES, INICIO, FIN, EstadoEmision.PROGRAMADO);
    }

    // =======================================================================
    // Usuarios
    // =======================================================================

    @Test
    void guardar_un_usuario_devuelve_lo_que_dio_la_base_de_datos_y_no_lo_que_se_le_paso() {
        // El usuario entra SIN id, como cualquier alta. El id lo pone la base de
        // datos y solo viaja en la entidad devuelta.
        Usuario nuevo = new Usuario(null, "Ana", "ana@radiostack.local", "hash", RolUsuario.LOCUTOR, true);
        when(usuarioJpa.save(any(UsuarioEntity.class))).thenReturn(entidadUsuario(42L, "ana@radiostack.local"));

        Usuario guardado = new UsuarioRepositoryAdapter(usuarioJpa).save(nuevo);

        assertEquals(42L, guardado.getId().longValue(),
                "el adaptador ha devuelto el usuario de entrada, sin el id que genera la base de datos");
    }

    @Test
    void buscar_un_email_que_no_existe_devuelve_vacio() {
        when(usuarioJpa.findByEmail("nadie@radiostack.local")).thenReturn(Optional.empty());

        Optional<Usuario> resultado = new UsuarioRepositoryAdapter(usuarioJpa).findByEmail("nadie@radiostack.local");

        assertTrue(resultado.isEmpty());
    }

    @Test
    void buscar_por_email_pasa_el_email_tal_cual_y_mapea_el_resultado() {
        // Sin normalizar, sin recortar: si algun dia hay que pasarlo a minusculas
        // sera una decision, y este test se caera para recordarlo.
        when(usuarioJpa.findByEmail("Ana@RadioStack.local"))
                .thenReturn(Optional.of(entidadUsuario(42L, "Ana@RadioStack.local")));

        Optional<Usuario> resultado = new UsuarioRepositoryAdapter(usuarioJpa).findByEmail("Ana@RadioStack.local");

        assertEquals("Ana@RadioStack.local", resultado.orElseThrow().getEmail());
        verify(usuarioJpa).findByEmail("Ana@RadioStack.local");
    }

    @Test
    void listar_usuarios_mapea_todos_los_que_devuelve_el_repositorio() {
        when(usuarioJpa.findAll()).thenReturn(List.of(
                entidadUsuario(1L, "ana@radiostack.local"),
                entidadUsuario(2L, "bea@radiostack.local")));

        List<Usuario> usuarios = new UsuarioRepositoryAdapter(usuarioJpa).findAll();

        assertEquals(2, usuarios.size());
        assertEquals("ana@radiostack.local", usuarios.get(0).getEmail());
        assertEquals("bea@radiostack.local", usuarios.get(1).getEmail());
    }

    // =======================================================================
    // Locutores
    // =======================================================================

    @Test
    void guardar_un_locutor_conserva_el_id_generado_y_su_usuario() {
        Locutor nuevo = new Locutor(null, "La Voz",
                new Usuario(7L, "Ana", "ana@radiostack.local", "hash", RolUsuario.LOCUTOR, true));
        LocutorEntity devuelto = new LocutorEntity();
        devuelto.setId(3L);
        devuelto.setNombreArtistico("La Voz");
        devuelto.setUsuario(entidadUsuario(7L, "ana@radiostack.local"));
        when(locutorJpa.save(any(LocutorEntity.class))).thenReturn(devuelto);

        Locutor guardado = new LocutorRepositoryAdapter(locutorJpa).save(nuevo);

        assertEquals(3L, guardado.getId().longValue());
        assertEquals("ana@radiostack.local", guardado.getUsuario().getEmail());
    }

    @Test
    void buscar_un_locutor_que_no_existe_devuelve_vacio() {
        when(locutorJpa.findById(99L)).thenReturn(Optional.empty());

        assertTrue(new LocutorRepositoryAdapter(locutorJpa).findById(99L).isEmpty());
    }

    // =======================================================================
    // Programas
    // =======================================================================

    @Test
    void guardar_un_programa_conserva_el_id_generado() {
        Programa nuevo = new Programa(null, "Tardes de Radio", "Magazine", "Magazine", true);
        ProgramaEntity devuelto = new ProgramaEntity();
        devuelto.setId(11L);
        devuelto.setNombre("Tardes de Radio");
        when(programaJpa.save(any(ProgramaEntity.class))).thenReturn(devuelto);

        Programa guardado = new ProgramaRepositoryAdapter(programaJpa).save(nuevo);

        assertEquals(11L, guardado.getId().longValue());
        assertEquals("Tardes de Radio", guardado.getNombre());
    }

    @Test
    void borrar_un_programa_delega_el_id_sin_leer_nada_antes() {
        new ProgramaRepositoryAdapter(programaJpa).deleteById(11L);

        verify(programaJpa).deleteById(11L);
        // Un borrado que primero busca y luego borra hace dos viajes a la base de
        // datos para lo mismo, y abre una ventana entre la lectura y el borrado.
        verify(programaJpa, never()).findById(anyLong());
    }

    @Test
    void listar_programas_mapea_todos() {
        ProgramaEntity uno = new ProgramaEntity();
        uno.setId(11L);
        uno.setNombre("Tardes de Radio");
        when(programaJpa.findAll()).thenReturn(List.of(uno));

        List<Programa> programas = new ProgramaRepositoryAdapter(programaJpa).findAll();

        assertEquals(1, programas.size());
        assertEquals("Tardes de Radio", programas.get(0).getNombre());
    }

    // =======================================================================
    // Emisiones — el unico adaptador con logica propia
    // =======================================================================

    @Test
    void guardar_una_emision_sustituye_el_programa_mapeado_por_una_referencia_de_jpa() {
        // Esta es la unica linea de logica real de los seis adaptadores, y merece
        // explicacion: el mapeador construye un ProgramaEntity NUEVO a partir del
        // dominio, y guardar la emision con ese objeto haria que JPA lo tratara
        // como una entidad desligada y acabara duplicando el programa. Pidiendo
        // una referencia por id se guarda la clave ajena sin tocar el programa.
        Programa existente = new Programa(11L, "Tardes de Radio", null, "Magazine", true);
        Emision emision = new Emision(null, existente, DiaSemana.JUEVES, INICIO, FIN, EstadoEmision.PROGRAMADO);
        ProgramaEntity referencia = new ProgramaEntity();
        referencia.setId(11L);
        when(programaJpa.getReferenceById(11L)).thenReturn(referencia);
        when(emisionJpa.save(any(EmisionEntity.class))).thenReturn(entidadEmision(5L));

        new EmisionRepositoryAdapter(emisionJpa, programaJpa).save(emision);

        ArgumentCaptor<EmisionEntity> capturada = ArgumentCaptor.forClass(EmisionEntity.class);
        verify(emisionJpa).save(capturada.capture());
        assertSame(referencia, capturada.getValue().getPrograma(),
                "se ha guardado el programa recien mapeado en vez de la referencia de JPA");
    }

    @Test
    void una_emision_sin_programa_no_pide_ninguna_referencia() {
        when(emisionJpa.save(any(EmisionEntity.class))).thenReturn(entidadEmision(5L));

        new EmisionRepositoryAdapter(emisionJpa, programaJpa).save(emisionDeDominio(null));

        verify(programaJpa, never()).getReferenceById(anyLong());
    }

    @Test
    void un_programa_todavia_sin_id_tampoco_pide_referencia() {
        // Un programa que aun no se ha guardado no tiene id, y pedir una
        // referencia a null reventaria. El adaptador lo comprueba; este test
        // impide que esa comprobacion se caiga en una limpieza.
        Programa sinGuardar = new Programa(null, "Programa nuevo", null, "Magazine", true);
        Emision emision = new Emision(null, sinGuardar, DiaSemana.LUNES, INICIO, FIN, EstadoEmision.PROGRAMADO);
        when(emisionJpa.save(any(EmisionEntity.class))).thenReturn(entidadEmision(5L));

        new EmisionRepositoryAdapter(emisionJpa, programaJpa).save(emision);

        verify(programaJpa, never()).getReferenceById(anyLong());
    }

    @Test
    void el_rango_de_fechas_llega_al_repositorio_sin_tocar_y_en_el_mismo_orden() {
        // Intercambiar los dos argumentos es un fallo silencioso: la consulta
        // devuelve una lista vacia y parece que no hay emisiones.
        when(emisionJpa.findByRangoFechas(INICIO, FIN)).thenReturn(List.of(entidadEmision(5L)));

        List<Emision> emisiones = new EmisionRepositoryAdapter(emisionJpa, programaJpa)
                .findByRangoFechas(INICIO, FIN);

        assertEquals(1, emisiones.size());
        verify(emisionJpa).findByRangoFechas(INICIO, FIN);
    }

    // =======================================================================
    // Comentarios y chat — los dos que resuelven la emision antes de consultar
    // =======================================================================

    @Test
    void guardar_un_comentario_conserva_el_id_generado_y_su_estado() {
        Comentario nuevo = new Comentario(null, emisionDeDominio(5L), "oyente", "Gran programa",
                INICIO, EstadoComentario.VISIBLE);
        ComentarioEntity devuelto = new ComentarioEntity();
        devuelto.setId(9L);
        devuelto.setAutor("oyente");
        devuelto.setMensaje("Gran programa");
        devuelto.setTimestamp(INICIO);
        devuelto.setEstado(EstadoComentario.VISIBLE);
        when(comentarioJpa.save(any(ComentarioEntity.class))).thenReturn(devuelto);

        Comentario guardado = new ComentarioRepositoryAdapter(comentarioJpa, emisionJpa).save(nuevo);

        assertEquals(9L, guardado.getId().longValue());
        assertEquals(EstadoComentario.VISIBLE, guardado.getEstado());
    }

    @Test
    void pedir_los_comentarios_de_una_emision_que_no_existe_no_llega_a_consultar_comentarios() {
        // El adaptador resuelve primero la emision. Si no esta, tiene que parar
        // ahi: consultar comentarios con una emision nula devolveria una lista
        // vacia y haria pasar «esa emision no existe» por «no hay comentarios».
        when(emisionJpa.findById(99L)).thenReturn(Optional.empty());
        var adaptador = new ComentarioRepositoryAdapter(comentarioJpa, emisionJpa);
        Emision inexistente = emisionDeDominio(99L);

        assertThrows(IllegalArgumentException.class, () -> adaptador.findByEmision(inexistente));

        verifyNoInteractions(comentarioJpa);
    }

    @Test
    void los_comentarios_se_filtran_por_la_emision_resuelta_en_base_de_datos() {
        EmisionEntity emisionEnBd = entidadEmision(5L);
        ComentarioEntity comentario = new ComentarioEntity();
        comentario.setId(9L);
        comentario.setAutor("oyente");
        comentario.setEstado(EstadoComentario.VISIBLE);
        when(emisionJpa.findById(5L)).thenReturn(Optional.of(emisionEnBd));
        when(comentarioJpa.findByEmision(emisionEnBd)).thenReturn(List.of(comentario));

        List<Comentario> comentarios = new ComentarioRepositoryAdapter(comentarioJpa, emisionJpa)
                .findByEmision(emisionDeDominio(5L));

        assertEquals(1, comentarios.size());
        assertEquals("oyente", comentarios.get(0).getAutor());
        // La entidad que se usa para filtrar es la que vino de la base de datos,
        // no una construida a partir del objeto de dominio recibido.
        verify(comentarioJpa).findByEmision(emisionEnBd);
    }

    @Test
    void guardar_un_mensaje_de_chat_conserva_el_id_y_el_alias() {
        ChatMessage nuevo = new ChatMessage(null, emisionDeDominio(5L), "locutor@radiostack.local",
                "Entramos en directo", INICIO);
        ChatMessageEntity devuelto = new ChatMessageEntity();
        devuelto.setId(4L);
        devuelto.setAlias("locutor@radiostack.local");
        devuelto.setContenido("Entramos en directo");
        devuelto.setTimestamp(INICIO);
        when(chatJpa.save(any(ChatMessageEntity.class))).thenReturn(devuelto);

        ChatMessage guardado = new ChatMessageRepositoryAdapter(chatJpa, emisionJpa).save(nuevo);

        assertEquals(4L, guardado.getId().longValue());
        assertEquals("locutor@radiostack.local", guardado.getAlias());
    }

    @Test
    void pedir_el_chat_de_una_emision_que_no_existe_no_llega_a_consultar_mensajes() {
        when(emisionJpa.findById(99L)).thenReturn(Optional.empty());
        var adaptador = new ChatMessageRepositoryAdapter(chatJpa, emisionJpa);
        Emision inexistente = emisionDeDominio(99L);

        assertThrows(IllegalArgumentException.class, () -> adaptador.findByEmision(inexistente));

        verifyNoInteractions(chatJpa);
    }

    @Test
    void el_chat_se_filtra_por_la_emision_resuelta_en_base_de_datos() {
        EmisionEntity emisionEnBd = entidadEmision(5L);
        ChatMessageEntity mensaje = new ChatMessageEntity();
        mensaje.setId(4L);
        mensaje.setAlias("locutor@radiostack.local");
        mensaje.setContenido("Entramos en directo");
        when(emisionJpa.findById(5L)).thenReturn(Optional.of(emisionEnBd));
        when(chatJpa.findByEmision(emisionEnBd)).thenReturn(List.of(mensaje));

        List<ChatMessage> mensajes = new ChatMessageRepositoryAdapter(chatJpa, emisionJpa)
                .findByEmision(emisionDeDominio(5L));

        assertEquals(1, mensajes.size());
        assertEquals("locutor@radiostack.local", mensajes.get(0).getAlias());
        verify(chatJpa).findByEmision(emisionEnBd);
    }
}
