package com.example.soccer.service;

import com.example.soccer.Assemblers.EquipoAssembler;
import com.example.soccer.dto.EquipoDTO;
import com.example.soccer.model.Equipo;
import com.example.soccer.repository.EquipoRepository;
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
import static org.mockito.Mockito.mockStatic;

class EquipoServiceTest {

    @InjectMocks
    private EquipoService equipoService;

    @Mock
    private EquipoRepository equipoRepository;

    @Mock
    private EquipoAssembler equipoAssembler;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this); // Inicializar los mocks
    }

    @Test
    void guardarEquipos_debeGuardarCorrectamente() {
        // Datos de prueba del archivo CSV
        List<String[]> equiposCsv = new ArrayList<>();
        equiposCsv.add(new String[]{"EquipoA", "CiudadA", "2000-01-01"});

        // Simular que no existe un equipo con los mismos datos
        when(equipoRepository.existsByNombreAndCiudad("EquipoA", "CiudadA")).thenReturn(false);

        // Llamar al método bajo prueba
        equipoService.guardarEquipos(equiposCsv);

        // Verificar que se ha guardado correctamente
        verify(equipoRepository, times(1)).save(any(Equipo.class));
    }

    @Test
    void guardarEquipos_debeLanzarExcepcionSiEquipoYaExiste() {
        // Datos de prueba del archivo CSV
        List<String[]> equiposCsv = new ArrayList<>();
        equiposCsv.add(new String[]{"EquipoA", "CiudadA", "2000-01-01"});

        // Simular que el equipo ya existe
        when(equipoRepository.existsByNombreAndCiudad("EquipoA", "CiudadA")).thenReturn(true);

        // Verificar que se lanza una excepción
        Exception exception = assertThrows(RuntimeException.class, () -> equipoService.guardarEquipos(equiposCsv));
        assertEquals("El equipo EquipoA CiudadA ya existe.", exception.getMessage());
    }

    @Test
    void findByIdEquipo_debeRetornarEquipoSiExiste() {
        // Simular equipo existente
        Equipo equipo = new Equipo();
        equipo.setId(1L);
        equipo.setNombre("EquipoA");

        when(equipoRepository.findById(1L)).thenReturn(Optional.of(equipo));

        // Llamar al método bajo prueba
        Equipo resultado = equipoService.findByIdEquipo(1L);

        // Verificar que el equipo fue encontrado
        assertNotNull(resultado);
        assertEquals("EquipoA", resultado.getNombre());
    }

    @Test
    void findByIdEquipo_debeRetornarNullSiNoExiste() {
        // Simular que no existe equipo
        when(equipoRepository.findById(1L)).thenReturn(Optional.empty());

        // Llamar al método bajo prueba
        Equipo resultado = equipoService.findByIdEquipo(1L);

        // Verificar que el resultado es null
        assertNull(resultado);
    }


    @Test
    void findById_debeRetornarDTO() {
        // Simular equipo existente
        Equipo equipo = new Equipo();
        equipo.setId(1L);
        equipo.setNombre("EquipoA");

        EquipoDTO equipoDTO = new EquipoDTO();
        equipoDTO.setId(1L);
        equipoDTO.setNombre("EquipoA");

        // Configurar el mock para el repositorio
        when(equipoRepository.findById(1L)).thenReturn(Optional.of(equipo));

        // Usar mockStatic para mockear los métodos estáticos de EquipoAssembler
        try (var mockedStatic = mockStatic(EquipoAssembler.class)) {
            mockedStatic.when(() -> EquipoAssembler.equipoToDTO(equipo)).thenReturn(equipoDTO);

            // Llamar al método bajo prueba
            Optional<EquipoDTO> resultado = equipoService.findById(1L);

            // Verificar que el resultado contiene un equipo
            assertTrue(resultado.isPresent());
            assertEquals("EquipoA", resultado.get().getNombre());
        }
    }




    @Test
    void findAll_debeRetornarListaDeDTOs() {
        // Simular lista de equipos
        List<Equipo> equipos = new ArrayList<>();
        Equipo equipo1 = new Equipo();
        equipo1.setId(1L);
        equipo1.setNombre("EquipoA");
        equipos.add(equipo1);

        // Simular conversión a DTO
        EquipoDTO equipoDTO = new EquipoDTO();
        equipoDTO.setId(1L);
        equipoDTO.setNombre("EquipoA");

        // Configurar el mock para el repositorio
        when(equipoRepository.findAll()).thenReturn(equipos);

        // Usar mockStatic para mockear los métodos estáticos de EquipoAssembler
        try (var mockedStatic = mockStatic(EquipoAssembler.class)) {
            mockedStatic.when(() -> EquipoAssembler.equipoToDTO(equipo1)).thenReturn(equipoDTO);

            // Llamar al método bajo prueba
            List<EquipoDTO> resultado = equipoService.findAll();

            // Verificar que el resultado contiene un equipo
            assertFalse(resultado.isEmpty());
            assertEquals(1, resultado.size());
            assertEquals("EquipoA", resultado.get(0).getNombre());
        }
    }

    @Test
    void updateEquipo_debeActualizarCorrectamente() {
        // Simular equipo existente
        Equipo equipo = new Equipo();
        equipo.setId(1L);
        equipo.setNombre("EquipoA");
        equipo.setCiudad("CiudadA");

        EquipoDTO equipoDTO = new EquipoDTO();
        equipoDTO.setId(1L);
        equipoDTO.setNombre("EquipoB");
        equipoDTO.setCiudad("CiudadB");

        // Configurar el mock para el repositorio
        when(equipoRepository.findById(1L)).thenReturn(Optional.of(equipo));

        // Usar mockStatic para mockear los métodos estáticos de EquipoAssembler
        try (var mockedStatic = mockStatic(EquipoAssembler.class)) {
            // Configurar el comportamiento del método estático
            mockedStatic.when(() -> EquipoAssembler.dtoToEquipo(equipoDTO)).thenReturn(equipo);
            mockedStatic.when(() -> EquipoAssembler.equipoToDTO(equipo)).thenReturn(equipoDTO); // Asegurarse de que este comportamiento esté definido

            // Simular que no existe otro equipo con los mismos datos
            when(equipoRepository.existsByNombreAndCiudad("EquipoB", "CiudadB")).thenReturn(false);

            // Llamar al método bajo prueba
            Optional<EquipoDTO> resultado = equipoService.updateEquipo(equipoDTO);

            // Verificar que el equipo fue actualizado
            assertTrue(resultado.isPresent(), "El resultado debería contener un EquipoDTO.");
            assertEquals("EquipoB", resultado.get().getNombre());
        }
    }


    @Test
    void deleteEquipo_debeEliminarCorrectamente() {
        // Simular equipo existente
        Equipo equipo = new Equipo();
        equipo.setId(1L);
        equipo.setNombre("EquipoA");

        when(equipoRepository.findById(1L)).thenReturn(Optional.of(equipo));

        // Llamar al método bajo prueba
        equipoService.deleteEquipo(1L);

        // Verificar que se ha llamado al método delete
        verify(equipoRepository, times(1)).delete(equipo);
    }
}
