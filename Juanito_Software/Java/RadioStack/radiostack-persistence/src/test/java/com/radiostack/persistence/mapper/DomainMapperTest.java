package com.radiostack.persistence.mapper;

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
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * La frontera entre el dominio y la base de datos.
 *
 * Este mapeador traduce en las dos direcciones, campo a campo y a mano. Es el
 * sitio exacto donde un campo nuevo se cuela sin su pareja: se anade a la
 * entidad y al `toEntity`, se olvida el `toDomain`, y a partir de ahi el dato se
 * guarda bien y se lee vacio. Nada lo delata, porque no falla nada: simplemente
 * un valor deja de estar.
 *
 * Por eso los tests de ida y vuelta comprueban TODOS los campos de cada pareja y
 * no una muestra. Un test que compruebe tres de seis campos deja tres huecos por
 * los que ese fallo pasa igual.
 *
 * Son funciones puras: no hay Spring, ni PostgreSQL, ni dobles.
 */
class DomainMapperTest {

    private static final LocalDateTime INICIO = LocalDateTime.of(2026, 9, 12, 20, 0);
    private static final LocalDateTime FIN = LocalDateTime.of(2026, 9, 12, 22, 0);

    // -----------------------------------------------------------------------
    // Usuario
    // -----------------------------------------------------------------------

    @Test
    void un_usuario_conserva_sus_seis_campos_al_ir_y_volver() {
        Usuario original = new Usuario(7L, "Ana", "ana@radiostack.local", "hash-bcrypt", RolUsuario.ADMIN, true);

        Usuario vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertEquals(7L, vuelta.getId().longValue());
        assertEquals("Ana", vuelta.getNombre());
        assertEquals("ana@radiostack.local", vuelta.getEmail());
        assertEquals("hash-bcrypt", vuelta.getPasswordHash());
        assertEquals(RolUsuario.ADMIN, vuelta.getRol());
        assertTrue(vuelta.isActivo());
    }

    @Test
    void un_usuario_desactivado_no_revive_al_pasar_por_la_entidad() {
        // UsuarioEntity declara `private boolean activo = true`. Si el mapeador
        // dejara de copiar ese campo, el valor por defecto de la entidad taparia
        // el fallo y una cuenta dada de baja volveria activa desde la base de
        // datos. El caso `true` de arriba no lo detectaria nunca.
        Usuario baja = new Usuario(7L, "Ana", "ana@radiostack.local", "hash", RolUsuario.LOCUTOR, false);

        assertFalse(DomainMapper.toEntity(baja).isActivo());
        assertFalse(DomainMapper.toDomain(DomainMapper.toEntity(baja)).isActivo());
    }

    // -----------------------------------------------------------------------
    // Locutor
    // -----------------------------------------------------------------------

    @Test
    void un_locutor_arrastra_su_usuario_entero() {
        Locutor original = new Locutor(3L, "La Voz",
                new Usuario(7L, "Ana", "ana@radiostack.local", "hash", RolUsuario.LOCUTOR, true));

        Locutor vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertEquals(3L, vuelta.getId().longValue());
        assertEquals("La Voz", vuelta.getNombreArtistico());
        assertNotNull(vuelta.getUsuario(), "el locutor ha perdido su usuario por el camino");
        assertEquals("ana@radiostack.local", vuelta.getUsuario().getEmail());
        assertEquals(RolUsuario.LOCUTOR, vuelta.getUsuario().getRol());
    }

    @Test
    void un_locutor_sin_usuario_no_revienta() {
        Locutor huerfano = new Locutor(3L, "La Voz", null);

        Locutor vuelta = DomainMapper.toDomain(DomainMapper.toEntity(huerfano));

        assertNull(vuelta.getUsuario());
    }

    // -----------------------------------------------------------------------
    // Programa
    // -----------------------------------------------------------------------

    @Test
    void un_programa_conserva_sus_campos_y_sus_locutores() {
        Programa original = new Programa(11L, "Tardes de Radio", "Magazine vespertino", "Magazine", true);
        original.setLocutores(Set.of(
                new Locutor(3L, "La Voz", new Usuario(7L, "Ana", "ana@radiostack.local", "h", RolUsuario.LOCUTOR, true))));

        Programa vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertEquals(11L, vuelta.getId().longValue());
        assertEquals("Tardes de Radio", vuelta.getNombre());
        assertEquals("Magazine vespertino", vuelta.getDescripcion());
        assertEquals("Magazine", vuelta.getCategoria());
        assertTrue(vuelta.isActivo());
        assertEquals(1, vuelta.getLocutores().size());
        assertEquals("La Voz", vuelta.getLocutores().iterator().next().getNombreArtistico());
    }

    @Test
    void un_programa_desactivado_no_revive_al_pasar_por_la_entidad() {
        // Mismo motivo que con el usuario: ProgramaEntity tambien tiene
        // `activo = true` por defecto.
        Programa retirado = new Programa(11L, "Tardes de Radio", null, "Magazine", false);

        assertFalse(DomainMapper.toEntity(retirado).isActivo());
    }

    @Test
    void un_programa_con_la_lista_de_locutores_a_null_se_convierte_a_entidad_sin_romper() {
        Programa sinLista = new Programa(11L, "Tardes de Radio", null, "Magazine", true);
        sinLista.setLocutores(null);

        ProgramaEntity entidad = DomainMapper.toEntity(sinLista);

        // `toEntity` comprueba el null y deja la coleccion que la entidad trae por
        // defecto, que esta vacia. No es lo mismo que perder datos: no habia.
        assertNotNull(entidad.getLocutores());
        assertTrue(entidad.getLocutores().isEmpty());
    }

    @Test
    void en_el_sentido_contrario_esa_misma_lista_a_null_si_rompe() {
        // ASIMETRIA DELIBERADAMENTE DOCUMENTADA, no un comportamiento aprobado.
        //
        // `toEntity` hace `if (programa.getLocutores() != null)`. `toDomain` no
        // comprueba nada y llama directo a `entity.getLocutores().stream()`.
        //
        // Hoy no explota en produccion porque ProgramaEntity inicializa el campo
        // a `new HashSet<>()`, pero basta un `setLocutores(null)` —o una entidad
        // construida a mano— para que el camino de LECTURA, que es el que usa
        // todo el catalogo, lance NullPointerException.
        //
        // Si se decide hacer `toDomain` simetrico, este test debe cambiar a
        // esperar una coleccion vacia. Que tenga que cambiarse es justo la senal
        // de que el arreglo ha entrado a proposito y no de rebote.
        ProgramaEntity entidad = new ProgramaEntity();
        entidad.setLocutores(null);

        assertThrows(NullPointerException.class, () -> DomainMapper.toDomain(entidad));
    }

    // -----------------------------------------------------------------------
    // Emision
    // -----------------------------------------------------------------------

    @Test
    void una_emision_arrastra_las_cuatro_capas_anidadas() {
        // Emision -> Programa -> Locutor -> Usuario. Cuatro niveles, y cada salto
        // es una llamada distinta del mapeador: si uno se rompe, el de abajo se
        // pierde entero y los de arriba siguen pareciendo correctos.
        Usuario usuario = new Usuario(7L, "Ana", "ana@radiostack.local", "h", RolUsuario.LOCUTOR, true);
        Programa programa = new Programa(11L, "Tardes de Radio", "Magazine", "Magazine", true);
        programa.setLocutores(Set.of(new Locutor(3L, "La Voz", usuario)));
        Emision original = new Emision(5L, programa, DiaSemana.JUEVES, INICIO, FIN, EstadoEmision.EN_EMISION);

        Emision vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertEquals(5L, vuelta.getId().longValue());
        assertEquals(DiaSemana.JUEVES, vuelta.getDiaSemana());
        assertEquals(INICIO, vuelta.getHoraInicio());
        assertEquals(FIN, vuelta.getHoraFin());
        assertEquals(EstadoEmision.EN_EMISION, vuelta.getEstado());
        assertEquals("Tardes de Radio", vuelta.getPrograma().getNombre());
        assertEquals("La Voz", vuelta.getPrograma().getLocutores().iterator().next().getNombreArtistico());
        assertEquals("ana@radiostack.local",
                vuelta.getPrograma().getLocutores().iterator().next().getUsuario().getEmail());
    }

    @Test
    void una_emision_sin_programa_no_revienta() {
        Emision suelta = new Emision(5L, null, DiaSemana.LUNES, INICIO, FIN, EstadoEmision.PROGRAMADO);

        Emision vuelta = DomainMapper.toDomain(DomainMapper.toEntity(suelta));

        assertNull(vuelta.getPrograma());
        assertEquals(EstadoEmision.PROGRAMADO, vuelta.getEstado());
    }

    @Test
    void una_emision_pierde_sus_comentarios_al_pasar_por_la_entidad() {
        // Tambien documentado a proposito. El dominio Emision tiene una lista de
        // comentarios; EmisionEntity no tiene ese campo, asi que el viaje de ida
        // y vuelta la vacia.
        //
        // No es un fallo: los comentarios se leen por su propio repositorio. Pero
        // quien lea `emision.getComentarios()` sobre algo que viene de la base de
        // datos va a encontrar una lista vacia SIEMPRE, y mas vale que lo sepa
        // por un test que por una incidencia.
        Emision original = new Emision(5L, null, DiaSemana.LUNES, INICIO, FIN, EstadoEmision.PROGRAMADO);
        original.addComentario(new Comentario(1L, null, "oyente", "hola", INICIO, EstadoComentario.VISIBLE));
        assertEquals(1, original.getComentarios().size());

        Emision vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertTrue(vuelta.getComentarios().isEmpty());
    }

    // -----------------------------------------------------------------------
    // Comentario y ChatMessage
    // -----------------------------------------------------------------------

    @Test
    void un_comentario_conserva_sus_seis_campos_y_su_emision() {
        Emision emision = new Emision(5L, null, DiaSemana.VIERNES, INICIO, FIN, EstadoEmision.FINALIZADO);
        Comentario original = new Comentario(9L, emision, "oyente@correo.local", "Gran programa",
                INICIO, EstadoComentario.MODERADO);

        Comentario vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertEquals(9L, vuelta.getId().longValue());
        assertEquals("oyente@correo.local", vuelta.getAutor());
        assertEquals("Gran programa", vuelta.getMensaje());
        assertEquals(INICIO, vuelta.getTimestamp());
        assertEquals(EstadoComentario.MODERADO, vuelta.getEstado());
        assertEquals(5L, vuelta.getEmision().getId().longValue());
    }

    @Test
    void un_mensaje_de_chat_conserva_alias_contenido_y_sello_de_tiempo() {
        // El alias es la identidad del mensaje en el chat en directo. Que viaje
        // intacto hasta la base de datos importa mas de lo que parece: es lo que
        // los oyentes ven como autor.
        Emision emision = new Emision(5L, null, DiaSemana.SABADO, INICIO, FIN, EstadoEmision.EN_EMISION);
        ChatMessage original = new ChatMessage(4L, emision, "locutor@radiostack.local", "Entramos en directo", INICIO);

        ChatMessage vuelta = DomainMapper.toDomain(DomainMapper.toEntity(original));

        assertEquals(4L, vuelta.getId().longValue());
        assertEquals("locutor@radiostack.local", vuelta.getAlias());
        assertEquals("Entramos en directo", vuelta.getContenido());
        assertEquals(INICIO, vuelta.getTimestamp());
        assertEquals(5L, vuelta.getEmision().getId().longValue());
    }

    // -----------------------------------------------------------------------
    // Nulos
    // -----------------------------------------------------------------------

    @Test
    void toDomain_devuelve_null_ante_null_en_las_seis_parejas() {
        // Los adaptadores encadenan `.map(DomainMapper::toDomain)` sobre
        // Optionals y listas que pueden traer nulos. Si una de las seis dejara de
        // comprobarlo, el fallo saldria como NullPointerException en una consulta
        // cualquiera, lejos de aqui.
        assertNull(DomainMapper.toDomain((UsuarioEntity) null));
        assertNull(DomainMapper.toDomain((LocutorEntity) null));
        assertNull(DomainMapper.toDomain((ProgramaEntity) null));
        assertNull(DomainMapper.toDomain((EmisionEntity) null));
        assertNull(DomainMapper.toDomain((ComentarioEntity) null));
        assertNull(DomainMapper.toDomain((ChatMessageEntity) null));
    }

    @Test
    void toEntity_devuelve_null_ante_null_en_las_seis_parejas() {
        assertNull(DomainMapper.toEntity((Usuario) null));
        assertNull(DomainMapper.toEntity((Locutor) null));
        assertNull(DomainMapper.toEntity((Programa) null));
        assertNull(DomainMapper.toEntity((Emision) null));
        assertNull(DomainMapper.toEntity((Comentario) null));
        assertNull(DomainMapper.toEntity((ChatMessage) null));
    }
}
