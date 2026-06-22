package com.example.soccer.service;

import com.opencsv.CSVReader;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.*;


class CsvServiceTest {

    @InjectMocks
    private CsvService csvService;

    @Mock
    private JugadorService jugadorService;

    @Mock
    private EquipoService equipoService;

    @Mock
    private ParticipacionService participacionService;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void procesarJugadores_conArchivoValido_debeRetornarOK() throws IOException {
        // Simular el contenido del archivo CSV
        List<String[]> jugadoresCsv = new ArrayList<>();
        jugadoresCsv.add(new String[]{"Nombre", "Apellido", "Edad"});
        jugadoresCsv.add(new String[]{"Lionel", "Messi", "34"});

        // Ruta del archivo
        String ruta = "C:\\Users\\jbernaldez\\Desktop\\datos\\jugadores.csv";

        // Usar mockStatic para mockear el método estático leerCSV
        try (MockedStatic<CsvService> mockedStatic = mockStatic(CsvService.class)) {
            // Simular el método leerCSV para devolver datos válidos
            mockedStatic.when(() -> CsvService.leerCSV(ruta)).thenReturn(jugadoresCsv);

            // Llamar al método bajo prueba
            ResponseEntity<String> response = csvService.procesarJugadores(ruta);

            // Verificar el resultado
            assertEquals(HttpStatus.OK, response.getStatusCode(), "El estado de respuesta debería ser OK.");
            assertEquals("Jugadores procesados correctamente.", response.getBody(), "El cuerpo de la respuesta debería contener el mensaje correcto.");

            // Verificar que se haya llamado al método guardarJugadores
            verify(jugadorService).guardarJugadores(jugadoresCsv);
        }
    }

    @Test
    void procesarJugadores_conArchivoVacio_debeRetornarBadRequest() throws IOException {
        // Ruta del archivo
        String ruta = "C:\\Users\\jbernaldez\\Desktop\\datos\\jugadores.csv";

        // Usar mockStatic para mockear el método estático leerCSV
        try (MockedStatic<CsvService> mockedStatic = mockStatic(CsvService.class)) {
            // Simular el método leerCSV para devolver una lista vacía
            mockedStatic.when(() -> CsvService.leerCSV(ruta)).thenReturn(new ArrayList<>());

            // Llamar al método bajo prueba
            ResponseEntity<String> response = csvService.procesarJugadores(ruta);

            // Verificar el resultado
            assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode(), "El estado de respuesta debería ser BAD_REQUEST.");
            assertEquals("El archivo CSV de jugadores está vacío o no se pudo leer.", response.getBody(), "El cuerpo de la respuesta debería contener el mensaje correcto.");
        }
    }

    @Test
    void procesarJugadores_conErrorDeLectura_debeRetornarInternalServerError() throws IOException {
        // Ruta del archivo
        String ruta = "C:\\Users\\jbernaldez\\Desktop\\datos\\jugadores.csv";

        // Usar mockStatic para mockear el método estático leerCSV
        try (MockedStatic<CsvService> mockedStatic = mockStatic(CsvService.class)) {
            // Simular el método leerCSV para lanzar una excepción
            mockedStatic.when(() -> CsvService.leerCSV(ruta)).thenThrow(new IOException("Error de lectura"));

            // Llamar al método bajo prueba
            ResponseEntity<String> response = csvService.procesarJugadores(ruta);

            // Verificar el resultado
            assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode(), "El estado de respuesta debería ser INTERNAL_SERVER_ERROR.");
            assertEquals("Error al procesar el archivo CSV de jugadores.", response.getBody(), "El cuerpo de la respuesta debería contener el mensaje correcto.");
        }
    }

    @Test
    void procesarEquipos_conArchivoValido_debeRetornarOK() throws IOException {
        // Simular el contenido del archivo CSV
        List<String[]> equiposCsv = new ArrayList<>();
        equiposCsv.add(new String[]{"Nombre", "Ciudad"});
        equiposCsv.add(new String[]{"FC Barcelona", "Barcelona"});

        // Ruta del archivo
        String ruta = "C:\\Users\\jbernaldez\\Desktop\\datos\\equipos.csv";

        // Usar mockStatic para mockear el método estático leerCSV
        try (MockedStatic<CsvService> mockedStatic = mockStatic(CsvService.class)) {
            // Simular el método leerCSV para devolver datos válidos
            mockedStatic.when(() -> CsvService.leerCSV(ruta)).thenReturn(equiposCsv);

            // Llamar al método bajo prueba
            ResponseEntity<String> response = csvService.procesarEquipos(ruta);

            // Verificar el resultado
            assertEquals(HttpStatus.OK, response.getStatusCode(), "El estado de respuesta debería ser OK.");
            assertEquals("Equipos procesados correctamente.", response.getBody(), "El cuerpo de la respuesta debería contener el mensaje correcto.");

            // Verificar que se haya llamado al método guardarEquipos
            verify(equipoService, times(1)).guardarEquipos(equiposCsv);
        }
    }

    @Test
    void procesarParticipaciones_conArchivoValido_debeRetornarOK() throws IOException {
        // Simular el contenido del archivo CSV
        List<String[]> participacionesCsv = new ArrayList<>();
        participacionesCsv.add(new String[]{"Jugador", "Equipo"});
        participacionesCsv.add(new String[]{"Lionel Messi", "FC Barcelona"});

        // Ruta del archivo
        String ruta = "C:\\Users\\jbernaldez\\Desktop\\datos\\participaciones.csv";

        // Usar mockStatic para mockear el método estático leerCSV
        try (MockedStatic<CsvService> mockedStatic = mockStatic(CsvService.class)) {
            // Simular el método leerCSV para devolver datos válidos
            mockedStatic.when(() -> CsvService.leerCSV(ruta)).thenReturn(participacionesCsv);

            // Llamar al método bajo prueba
            ResponseEntity<String> response = csvService.procesarParticipaciones(ruta);

            // Verificar el resultado
            assertEquals(HttpStatus.OK, response.getStatusCode(), "El estado de respuesta debería ser OK.");
            assertEquals("Participaciones procesadas correctamente.", response.getBody(), "El cuerpo de la respuesta debería contener el mensaje correcto.");

            // Verificar que se haya llamado al método guardarParticipaciones
            verify(participacionService, times(1)).guardarParticipaciones(participacionesCsv);
        }
    }
}
