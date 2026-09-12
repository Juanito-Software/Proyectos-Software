package com.radiostack.api.service;

import com.radiostack.core.domain.DiaSemana;
import com.radiostack.core.domain.Emision;
import com.radiostack.core.domain.EstadoEmision;
import com.radiostack.core.domain.Locutor;
import com.radiostack.core.domain.Programa;
import com.radiostack.core.port.EmisionRepository;
import com.radiostack.core.port.ProgramaRepository;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Programas, emisiones y parrilla: el catalogo de la radio.
 *
 * Son servicios finos, y aun asi tienen tres decisiones que se pueden romper sin
 * darse cuenta: que crear nunca actualice, que actualizar no borre lo que no
 * venia en la peticion, y que la parrilla cubra los dias completos que se le
 * piden.
 */
@ExtendWith(MockitoExtension.class)
class CatalogoServiciosTest {

    @Mock
    private ProgramaRepository programaRepository;
    @Mock
    private EmisionRepository emisionRepository;

    @Nested
    class Programas {

        private ProgramaServiceImpl servicio() {
            return new ProgramaServiceImpl(programaRepository);
        }

        private Programa programa(Long id, String nombre) {
            Programa p = new Programa();
            p.setId(id);
            p.setNombre(nombre);
            p.setDescripcion("descripcion");
            p.setCategoria("musica");
            p.setActivo(true);
            return p;
        }

        @Test
        void crear_ignora_el_id_que_llegue() {
            // Con el id puesto, `save` seria un UPDATE y crear un programa podria
            // sobrescribir otro que ya existe.
            when(programaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            servicio().crearPrograma(programa(99L, "Nuevo"));

            ArgumentCaptor<Programa> guardado = ArgumentCaptor.forClass(Programa.class);
            verify(programaRepository).save(guardado.capture());
            assertNull(guardado.getValue().getId());
        }

        @Test
        void actualizar_uno_que_no_existe_es_un_error_y_no_lo_crea() {
            when(programaRepository.findById(99L)).thenReturn(Optional.empty());

            assertThrows(IllegalArgumentException.class, () -> servicio().actualizarPrograma(99L, programa(null, "X")));
            verify(programaRepository, never()).save(any());
        }

        @Test
        void actualizar_copia_los_campos_sobre_el_programa_existente() {
            Programa existente = programa(5L, "Antiguo");
            when(programaRepository.findById(5L)).thenReturn(Optional.of(existente));
            when(programaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            Programa cambios = programa(null, "Nuevo nombre");
            cambios.setCategoria("tertulia");
            cambios.setActivo(false);
            servicio().actualizarPrograma(5L, cambios);

            ArgumentCaptor<Programa> guardado = ArgumentCaptor.forClass(Programa.class);
            verify(programaRepository).save(guardado.capture());
            // Se guarda la fila existente, no una nueva: el id se mantiene.
            assertEquals(5L, guardado.getValue().getId().longValue());
            assertEquals("Nuevo nombre", guardado.getValue().getNombre());
            assertEquals("tertulia", guardado.getValue().getCategoria());
            assertFalse(guardado.getValue().isActivo());
        }

        @Test
        void actualizar_sin_locutores_no_borra_los_que_ya_tenia() {
            // El servicio solo toca los locutores si vienen en la peticion. Si los
            // sustituyera siempre, editar el nombre de un programa desde un formulario
            // que no los incluye dejaria el programa sin locutores.
            Programa existente = programa(5L, "Antiguo");
            Locutor locutor = new Locutor();
            locutor.setId(1L);
            existente.setLocutores(Set.of(locutor));
            when(programaRepository.findById(5L)).thenReturn(Optional.of(existente));
            when(programaRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            Programa cambios = programa(null, "Nuevo nombre");
            cambios.setLocutores(null);
            servicio().actualizarPrograma(5L, cambios);

            ArgumentCaptor<Programa> guardado = ArgumentCaptor.forClass(Programa.class);
            verify(programaRepository).save(guardado.capture());
            assertEquals(1, guardado.getValue().getLocutores().size());
        }

        @Test
        void eliminar_delega_en_el_repositorio() {
            servicio().eliminarPrograma(5L);

            verify(programaRepository).deleteById(5L);
        }

        @Test
        void obtener_y_listar_delegan_en_el_repositorio() {
            Programa p = programa(5L, "Uno");
            when(programaRepository.findById(5L)).thenReturn(Optional.of(p));
            when(programaRepository.findAll()).thenReturn(List.of(p));

            assertSame(p, servicio().obtenerPrograma(5L).orElseThrow());
            assertEquals(1, servicio().listarProgramas().size());
        }
    }

    @Nested
    class Emisiones {

        private EmisionServiceImpl servicio() {
            return new EmisionServiceImpl(emisionRepository);
        }

        private Emision emision(Long id, EstadoEmision estado) {
            Emision e = new Emision();
            e.setId(id);
            e.setDiaSemana(DiaSemana.LUNES);
            e.setHoraInicio(LocalDateTime.of(2026, 9, 14, 20, 0));
            e.setHoraFin(LocalDateTime.of(2026, 9, 14, 22, 0));
            e.setEstado(estado);
            return e;
        }

        @Test
        void crear_ignora_el_id_que_llegue() {
            when(emisionRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            servicio().crearEmision(emision(99L, EstadoEmision.PROGRAMADO));

            ArgumentCaptor<Emision> guardada = ArgumentCaptor.forClass(Emision.class);
            verify(emisionRepository).save(guardada.capture());
            assertNull(guardada.getValue().getId());
        }

        @Test
        void actualizar_una_que_no_existe_es_un_error_y_no_la_crea() {
            when(emisionRepository.findById(99L)).thenReturn(Optional.empty());

            assertThrows(IllegalArgumentException.class,
                    () -> servicio().actualizarEmision(99L, emision(null, EstadoEmision.EN_EMISION)));
            verify(emisionRepository, never()).save(any());
        }

        @Test
        void actualizar_cambia_el_estado_sobre_la_emision_existente() {
            // Pasar a EN_EMISION es lo que pone una emision «en directo»: conviene que
            // el cambio se guarde sobre la fila que ya existe y no como una nueva.
            Emision existente = emision(5L, EstadoEmision.PROGRAMADO);
            when(emisionRepository.findById(5L)).thenReturn(Optional.of(existente));
            when(emisionRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            servicio().actualizarEmision(5L, emision(null, EstadoEmision.EN_EMISION));

            ArgumentCaptor<Emision> guardada = ArgumentCaptor.forClass(Emision.class);
            verify(emisionRepository).save(guardada.capture());
            assertEquals(5L, guardada.getValue().getId().longValue());
            assertEquals(EstadoEmision.EN_EMISION, guardada.getValue().getEstado());
        }

        @Test
        void obtener_delega_en_el_repositorio() {
            Emision e = emision(5L, EstadoEmision.PROGRAMADO);
            when(emisionRepository.findById(5L)).thenReturn(Optional.of(e));

            assertSame(e, servicio().obtenerEmision(5L).orElseThrow());
        }
    }

    @Nested
    class Parrilla {

        private ParrillaServiceImpl servicio() {
            return new ParrillaServiceImpl(emisionRepository);
        }

        @Test
        void pide_el_rango_desde_el_primer_instante_hasta_el_ultimo_del_dia() {
            // Las horas salen de fechas sin hora, asi que el servicio las completa. Si
            // usara `to.atStartOfDay()`, las emisiones del ultimo dia pedido
            // desaparecerian de la parrilla.
            when(emisionRepository.findByRangoFechas(any(), any())).thenReturn(List.of());

            servicio().obtenerParrilla(LocalDate.of(2026, 9, 14), LocalDate.of(2026, 9, 20));

            ArgumentCaptor<LocalDateTime> desde = ArgumentCaptor.forClass(LocalDateTime.class);
            ArgumentCaptor<LocalDateTime> hasta = ArgumentCaptor.forClass(LocalDateTime.class);
            verify(emisionRepository).findByRangoFechas(desde.capture(), hasta.capture());
            assertEquals(LocalDateTime.of(2026, 9, 14, 0, 0), desde.getValue());
            assertEquals(LocalDate.of(2026, 9, 20).atTime(23, 59, 59, 999_999_999), hasta.getValue());
        }

        @Test
        void un_solo_dia_sigue_cubriendo_las_24_horas() {
            when(emisionRepository.findByRangoFechas(any(), any())).thenReturn(List.of());

            servicio().obtenerParrilla(LocalDate.of(2026, 9, 14), LocalDate.of(2026, 9, 14));

            ArgumentCaptor<LocalDateTime> desde = ArgumentCaptor.forClass(LocalDateTime.class);
            ArgumentCaptor<LocalDateTime> hasta = ArgumentCaptor.forClass(LocalDateTime.class);
            verify(emisionRepository).findByRangoFechas(desde.capture(), hasta.capture());
            assertEquals(0, desde.getValue().getHour());
            assertEquals(23, hasta.getValue().getHour());
        }

        @Test
        void devuelve_las_emisiones_que_encuentra() {
            Emision e = new Emision();
            when(emisionRepository.findByRangoFechas(any(), any())).thenReturn(List.of(e));

            List<Emision> parrilla = servicio().obtenerParrilla(LocalDate.of(2026, 9, 14), LocalDate.of(2026, 9, 20));

            assertEquals(1, parrilla.size());
            assertSame(e, parrilla.get(0));
        }
    }
}
