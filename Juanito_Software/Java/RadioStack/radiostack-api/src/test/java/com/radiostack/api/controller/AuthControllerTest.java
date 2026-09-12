package com.radiostack.api.controller;

import com.radiostack.api.dto.AuthDTO;
import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.api.security.JwtService;
import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import com.radiostack.core.service.UsuarioService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Iniciar sesion y consultar quien soy.
 *
 * Se llama al controlador directamente, sin levantar Spring: lo que tiene es una
 * decision —si estas credenciales valen y que se devuelve— y eso no necesita
 * servidor. Las reglas de acceso por ruta son de SecurityConfig y se prueban
 * aparte.
 */
@ExtendWith(MockitoExtension.class)
class AuthControllerTest {

    @Mock
    private UsuarioService usuarioService;
    @Mock
    private PasswordEncoder passwordEncoder;
    @Mock
    private JwtService jwtService;

    private AuthController controlador() {
        return new AuthController(usuarioService, passwordEncoder, jwtService);
    }

    private static Usuario usuario(boolean activo) {
        Usuario u = new Usuario();
        u.setId(7L);
        u.setNombre("Juanito DJ");
        u.setEmail("locutor@radiostack.local");
        u.setPasswordHash("$2a$10$HASH");
        u.setRol(RolUsuario.LOCUTOR);
        u.setActivo(activo);
        return u;
    }

    private static AuthDTO.LoginRequest credenciales(String password) {
        AuthDTO.LoginRequest req = new AuthDTO.LoginRequest();
        req.setEmail("locutor@radiostack.local");
        req.setPassword(password);
        return req;
    }

    @Test
    void con_las_credenciales_buenas_devuelve_el_token_y_el_usuario() {
        when(usuarioService.buscarPorEmail("locutor@radiostack.local")).thenReturn(Optional.of(usuario(true)));
        when(passwordEncoder.matches("secreto", "$2a$10$HASH")).thenReturn(true);
        when(jwtService.emitir(any())).thenReturn("token-firmado");

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador().login(credenciales("secreto"));

        assertEquals(200, respuesta.getStatusCode().value());
        assertNotNull(respuesta.getBody());
        assertEquals("token-firmado", respuesta.getBody().getToken());
        assertEquals("locutor@radiostack.local", respuesta.getBody().getUsuario().getEmail());
    }

    @Test
    void el_token_que_se_devuelve_va_pelado_sin_el_prefijo_Bearer() {
        // El prefijo pertenece a la cabecera HTTP, no al token, y lo pone el cliente
        // al enviarlo. Antes iba incrustado en la cadena ("Bearer-demo-<id>"), lo que
        // mezclaba las dos cosas.
        when(usuarioService.buscarPorEmail(anyString())).thenReturn(Optional.of(usuario(true)));
        when(passwordEncoder.matches(anyString(), anyString())).thenReturn(true);
        when(jwtService.emitir(any())).thenReturn("token-firmado");

        String token = controlador().login(credenciales("secreto")).getBody().getToken();

        assertEquals("token-firmado", token);
    }

    @Test
    void con_la_contrasena_equivocada_responde_401_y_no_emite_token() {
        when(usuarioService.buscarPorEmail(anyString())).thenReturn(Optional.of(usuario(true)));
        when(passwordEncoder.matches("mala", "$2a$10$HASH")).thenReturn(false);

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador().login(credenciales("mala"));

        assertEquals(401, respuesta.getStatusCode().value());
        assertNull(respuesta.getBody());
        verify(jwtService, never()).emitir(any());
    }

    @Test
    void con_un_email_que_no_existe_responde_401_sin_comprobar_contrasena() {
        when(usuarioService.buscarPorEmail(anyString())).thenReturn(Optional.empty());

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador().login(credenciales("secreto"));

        assertEquals(401, respuesta.getStatusCode().value());
        verify(passwordEncoder, never()).matches(anyString(), anyString());
        verify(jwtService, never()).emitir(any());
    }

    @Test
    void una_cuenta_desactivada_no_entra_ni_con_la_contrasena_buena() {
        // Desactivar una cuenta tiene que servir de algo: es la unica forma de
        // cerrarle la puerta a alguien, porque los JWT ya emitidos no se revocan.
        when(usuarioService.buscarPorEmail(anyString())).thenReturn(Optional.of(usuario(false)));
        when(passwordEncoder.matches(anyString(), anyString())).thenReturn(true);

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador().login(credenciales("secreto"));

        assertEquals(401, respuesta.getStatusCode().value());
        verify(jwtService, never()).emitir(any());
    }

    @Test
    void me_sin_identidad_responde_401() {
        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador().me(null);

        assertEquals(401, respuesta.getStatusCode().value());
        verify(usuarioService, never()).obtenerPorId(any());
    }

    @Test
    void me_devuelve_el_usuario_actual_de_la_base_de_datos() {
        when(usuarioService.obtenerPorId(7L)).thenReturn(Optional.of(usuario(true)));

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador()
                .me(new UsuarioAutenticado(7L, "locutor@radiostack.local", "LOCUTOR"));

        assertEquals(200, respuesta.getStatusCode().value());
        assertEquals("Juanito DJ", respuesta.getBody().getUsuario().getNombre());
        // `me` no reemite token: solo traduce el usuario del token a su estado actual.
        assertNull(respuesta.getBody().getToken());
    }

    @Test
    void me_con_un_token_valido_de_una_cuenta_ya_desactivada_responde_401() {
        // Un JWT sigue siendo valido despues de desactivar la cuenta, porque no se
        // puede revocar. Por eso se comprueba contra la base de datos en cada
        // llamada; si no, el desactivado seguiria dentro hasta que caducara.
        when(usuarioService.obtenerPorId(7L)).thenReturn(Optional.of(usuario(false)));

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador()
                .me(new UsuarioAutenticado(7L, "locutor@radiostack.local", "LOCUTOR"));

        assertEquals(401, respuesta.getStatusCode().value());
        assertNull(respuesta.getBody());
    }

    @Test
    void me_con_un_usuario_que_ya_no_esta_en_la_base_de_datos_responde_401() {
        when(usuarioService.obtenerPorId(7L)).thenReturn(Optional.empty());

        ResponseEntity<AuthDTO.LoginResponse> respuesta = controlador()
                .me(new UsuarioAutenticado(7L, "borrado@radiostack.local", "LOCUTOR"));

        assertEquals(401, respuesta.getStatusCode().value());
    }
}
