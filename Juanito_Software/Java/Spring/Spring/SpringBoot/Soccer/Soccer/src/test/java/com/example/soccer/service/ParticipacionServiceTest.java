package com.example.soccer.service;

import com.example.soccer.Assemblers.ParticipacionAssembler;
import com.example.soccer.dto.ParticipacionDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.model.Jugador;
import com.example.soccer.model.Participacion;
import com.example.soccer.repository.ParticipacionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class ParticipacionServiceTest {

    @InjectMocks
    private ParticipacionService participacionService;

    @Mock
    private ParticipacionRepository participacionRepository;

    @Mock
    private JugadorService jugadorService;

    @Mock
    private EquipoService equipoService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void guardarParticipaciones() {
        List<String[]> participacionesCsv = List.of(
                new String[]{"1", "2", "2023-01-01", "2024-01-01", "10"},
                new String[]{"3", "4", "2023-01-01", "2024-01-01", "7"}
        );

        Jugador jugador1 = new Jugador();
        Equipo equipo1 = new Equipo();
        Jugador jugador2 = new Jugador();
        Equipo equipo2 = new Equipo();

        when(jugadorService.findByIdJugador(1L)).thenReturn(jugador1);
        when(equipoService.findByIdEquipo(2L)).thenReturn(equipo1);
        when(jugadorService.findByIdJugador(3L)).thenReturn(jugador2);
        when(equipoService.findByIdEquipo(4L)).thenReturn(equipo2);
        when(participacionRepository.existsByEquipoAndDorsalAndFechas(any(), anyInt(), any(), any()))
                .thenReturn(false);

        participacionService.guardarParticipaciones(participacionesCsv);

        verify(participacionRepository, times(2)).save(any(Participacion.class));
    }

    @Test
    void findById() {
        Participacion participacion = new Participacion();
        participacion.setId(1L);

        // Simular el comportamiento del repositorio
        when(participacionRepository.findById(1L)).thenReturn(Optional.of(participacion));

        // Usar mockStatic para mockear los métodos estáticos de ParticipacionAssembler
        try (var mockedStatic = mockStatic(ParticipacionAssembler.class)) {
            // Configurar el comportamiento del método estático
            mockedStatic.when(() -> ParticipacionAssembler.participacionToDTO(participacion)).thenReturn(new ParticipacionDTO());

            // Llamar al método bajo prueba
            ParticipacionDTO result = participacionService.findById(1L);

            // Verificar el resultado
            assertNotNull(result);
            verify(participacionRepository, times(1)).findById(1L);
            mockedStatic.verify(() -> ParticipacionAssembler.participacionToDTO(participacion), times(1)); // Verifica que se llamó al método estático
        }
    }

    @Test
    void findAll() {
        List<Participacion> participaciones = List.of(new Participacion(), new Participacion());

        // Configurar el mock para el repositorio
        when(participacionRepository.findAll()).thenReturn(participaciones);

        // Usar mockStatic para mockear los métodos estáticos de ParticipacionAssembler
        try (var mockedStatic = mockStatic(ParticipacionAssembler.class)) {
            // Configurar el comportamiento del método estático
            mockedStatic.when(() -> ParticipacionAssembler.participacionToDTO(any())).thenReturn(new ParticipacionDTO());

            // Llamar al método bajo prueba
            List<ParticipacionDTO> result = participacionService.findAll();

            // Verificar el resultado
            assertEquals(2, result.size());
            verify(participacionRepository, times(1)).findAll();
            mockedStatic.verify(() -> ParticipacionAssembler.participacionToDTO(any()), times(2)); // Verifica que se haya llamado 2 veces
        }
    }

    @Test
    void updateParticipacion() {
        Participacion participacion = new Participacion();
        participacion.setId(1L);
        // Cambiar la fecha de inicio a una fecha futura para que la prueba funcione
        participacion.setFechaInicio(LocalDate.of(2025, 1, 1)); // Cambiar aquí

        ParticipacionDTO participacionDTO = new ParticipacionDTO();
        participacionDTO.setId(1L);
        participacionDTO.setFechaInicio(LocalDate.of(2024, 1, 1));
        participacionDTO.setFechaFin(LocalDate.of(2024, 12, 31));
        participacionDTO.setDorsal(10);
        // Asumir que necesitas agregar jugadorId y equipoId también
        participacionDTO.setJugadorId(1L);
        participacionDTO.setEquipoId(1L);

        when(participacionRepository.findById(1L)).thenReturn(Optional.of(participacion));
        when(jugadorService.findByIdJugador(anyLong())).thenReturn(new Jugador());
        when(equipoService.findByIdEquipo(anyLong())).thenReturn(new Equipo());
        when(participacionRepository.save(any())).thenReturn(participacion);

        Optional<ParticipacionDTO> result = participacionService.updateParticipacion(participacionDTO);

        assertTrue(result.isPresent(), "El resultado debe estar presente.");
        verify(participacionRepository, times(1)).save(any(Participacion.class));
    }

    @Test
    void deleteParticipacion() {
        Participacion participacion = new Participacion();
        participacion.setId(1L);
        participacion.setFechaInicio(LocalDate.now().plusDays(1));

        when(participacionRepository.findById(1L)).thenReturn(Optional.of(participacion));
        doNothing().when(participacionRepository).delete(any(Participacion.class));

        participacionService.deleteParticipacion(1L);

        verify(participacionRepository, times(1)).delete(participacion);
    }

    @Test
    void deleteParticipacionAfterStart() {
        Participacion participacion = new Participacion();
        participacion.setId(1L);
        participacion.setFechaInicio(LocalDate.now().minusDays(1));

        when(participacionRepository.findById(1L)).thenReturn(Optional.of(participacion));
        when(participacionRepository.save(any())).thenReturn(participacion);

        participacionService.deleteParticipacion(1L);

        verify(participacionRepository, times(1)).save(participacion);
        assertFalse(participacion.isActivo());
    }
}
