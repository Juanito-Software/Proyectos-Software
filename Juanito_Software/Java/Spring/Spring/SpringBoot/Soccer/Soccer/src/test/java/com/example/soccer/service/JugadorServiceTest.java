package com.example.soccer.service;

import com.example.soccer.Assemblers.JugadorAssembler;
import com.example.soccer.dto.JugadorDTO;
import com.example.soccer.model.Jugador;
import com.example.soccer.repository.JugadorRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.MockitoAnnotations;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class JugadorServiceTest {

    @InjectMocks
    private JugadorService jugadorService;

    @Mock
    private JugadorRepository jugadorRepository;

    @Mock
    private JugadorAssembler jugadorAssembler;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void guardarJugadores() {
        List<String[]> jugadoresCsv = List.of(
                new String[]{"Lionel", "Messi", "1987-06-24", "Delantero"},
                new String[]{"Cristiano", "Ronaldo", "1985-02-05", "Delantero"}
        );

        when(jugadorRepository.existsByNombreAndApellidoAndFechaNac(anyString(), anyString(), any(LocalDate.class)))
                .thenReturn(false);

        String resultado = jugadorService.guardarJugadores(jugadoresCsv);

        assertEquals("Jugadores guardados exitosamente.", resultado);
        verify(jugadorRepository, times(2)).save(any(Jugador.class));
    }

    @Test
    void findByIdJugador() {
        Jugador jugador = new Jugador();
        jugador.setId(1L);
        jugador.setNombre("Lionel");
        jugador.setApellido("Messi");
        jugador.setFechaNac(LocalDate.of(1987, 6, 24));
        jugador.setPosicion("Delantero");

        when(jugadorRepository.findById(1L)).thenReturn(Optional.of(jugador));

        Jugador result = jugadorService.findByIdJugador(1L);
        assertNotNull(result);
        assertEquals("Lionel", result.getNombre());
    }

    @Test
    void findById() {
        Jugador jugador = new Jugador();
        jugador.setId(1L);

        // Simular el repositorio
        when(jugadorRepository.findById(1L)).thenReturn(Optional.of(jugador));

        // Usar mockStatic para mockear el método estático jugadorToDTO
        try (MockedStatic<JugadorAssembler> mockedStatic = mockStatic(JugadorAssembler.class)) {
            // Configurar el comportamiento del método estático
            mockedStatic.when(() -> JugadorAssembler.jugadorToDTO(jugador)).thenReturn(new JugadorDTO());

            // Llamar al método bajo prueba
            JugadorDTO result = jugadorService.findById(1L);

            // Verificar que el resultado no sea nulo
            assertNotNull(result);
        }
    }

    @Test
    void findAll() {
        // Crear lista de jugadores simulados
        List<Jugador> jugadores = List.of(new Jugador(), new Jugador());
        when(jugadorRepository.findAll()).thenReturn(jugadores);

        // Usar mockStatic para mockear métodos estáticos de JugadorAssembler
        try (MockedStatic<JugadorAssembler> mockedStatic = mockStatic(JugadorAssembler.class)) {
            // Simular el método jugadorToDTO
            mockedStatic.when(() -> JugadorAssembler.jugadorToDTO(any(Jugador.class))).thenReturn(new JugadorDTO());

            // Llamar al método bajo prueba
            List<JugadorDTO> result = jugadorService.findAll();

            // Verificar resultados
            assertEquals(2, result.size());
        }
    }

    @Test
    void updateJugador() {
        JugadorDTO jugadorDTO = new JugadorDTO();
        jugadorDTO.setId(1L);
        jugadorDTO.setNombre("Lionel");

        Jugador jugador = new Jugador();
        jugador.setId(1L);

        // Configurar el mock del repositorio
        when(jugadorRepository.findById(1L)).thenReturn(Optional.of(jugador));

        // Usar mockStatic para mockear los métodos estáticos de JugadorAssembler
        try (MockedStatic<JugadorAssembler> mockedStatic = mockStatic(JugadorAssembler.class)) {
            // Configurar el comportamiento del método estático dtoToJugador
            mockedStatic.when(() -> JugadorAssembler.dtoToJugador(jugadorDTO)).thenReturn(jugador);
            // Configurar el comportamiento del método estático jugadorToDTO
            mockedStatic.when(() -> JugadorAssembler.jugadorToDTO(jugador)).thenReturn(jugadorDTO);

            // Simular el comportamiento de save
            when(jugadorRepository.save(jugador)).thenReturn(jugador);

            // Llamar al método bajo prueba
            JugadorDTO result = jugadorService.updateJugador(jugadorDTO);

            // Verificar el resultado
            assertNotNull(result);
            assertEquals("Lionel", result.getNombre());
        }
    }

    @Test
    void deleteJugador() {
        Jugador jugador = new Jugador();
        jugador.setId(1L);

        when(jugadorRepository.findById(1L)).thenReturn(Optional.of(jugador));
        doNothing().when(jugadorRepository).delete(jugador);

        jugadorService.deleteJugador(1L);
        verify(jugadorRepository, times(1)).delete(jugador);
    }
}
