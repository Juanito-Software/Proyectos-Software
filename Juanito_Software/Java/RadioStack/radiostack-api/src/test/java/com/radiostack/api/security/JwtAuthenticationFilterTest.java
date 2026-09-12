package com.radiostack.api.security;

import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Date;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * El filtro que traduce la cabecera Authorization en una identidad.
 *
 * La regla de diseño que estos tests protegen: el filtro NUNCA rechaza una
 * peticion. Si no hay token, o no vale, deja el contexto vacio y sigue; quien
 * decide si esa ruta exige autenticacion es SecurityConfig. Un filtro que
 * devolviera 401 por su cuenta repartiria las reglas de acceso en dos sitios, y
 * las rutas publicas (la parrilla, los programas) dejarian de funcionar para
 * quien enviara un token caducado.
 */
class JwtAuthenticationFilterTest {

    private static final String SECRETO = Base64.getEncoder()
            .encodeToString("clave-de-prueba-de-48-bytes-para-firmar-con-hmac!".getBytes(StandardCharsets.UTF_8));

    private final JwtService jwtService = new JwtService(SECRETO, 3600);
    private final JwtAuthenticationFilter filtro = new JwtAuthenticationFilter(jwtService);

    @AfterEach
    void limpiarContexto() {
        // El contexto de seguridad vive en un ThreadLocal: sin limpiarlo, el test
        // siguiente heredaria la identidad del anterior y pasaria por el motivo
        // equivocado.
        SecurityContextHolder.clearContext();
    }

    private static Usuario usuario() {
        Usuario u = new Usuario();
        u.setId(7L);
        u.setEmail("locutor@radiostack.local");
        u.setRol(RolUsuario.LOCUTOR);
        u.setActivo(true);
        return u;
    }

    /** Lanza el filtro con la cabecera indicada (null = sin cabecera). */
    private Authentication filtrarCon(String cabecera) throws Exception {
        MockHttpServletRequest peticion = new MockHttpServletRequest("GET", "/api/v1/programas");
        if (cabecera != null) {
            peticion.addHeader("Authorization", cabecera);
        }
        MockFilterChain cadena = new MockFilterChain();

        filtro.doFilter(peticion, new MockHttpServletResponse(), cadena);

        // La cadena tiene que continuar siempre: el filtro informa, no decide.
        assertNotNull(cadena.getRequest(), "el filtro ha cortado la cadena");
        return SecurityContextHolder.getContext().getAuthentication();
    }

    /** Token firmado con la clave buena pero con los claims que se quieran. */
    private String tokenConClaims(String sub, String email, String rol) {
        SecretKey clave = Keys.hmacShaKeyFor(Base64.getDecoder().decode(SECRETO));
        var builder = Jwts.builder().subject(sub).expiration(new Date(System.currentTimeMillis() + 60_000));
        if (email != null) builder.claim("email", email);
        if (rol != null) builder.claim("rol", rol);
        return builder.signWith(clave).compact();
    }

    @Test
    void con_un_token_valido_deja_al_usuario_en_el_contexto() throws Exception {
        Authentication auth = filtrarCon("Bearer " + jwtService.emitir(usuario()));

        assertNotNull(auth);
        UsuarioAutenticado autenticado = assertInstanceOf(UsuarioAutenticado.class, auth.getPrincipal());
        assertEquals(7L, autenticado.id().longValue());
        assertEquals("locutor@radiostack.local", autenticado.email());
        assertEquals("LOCUTOR", autenticado.rol());
    }

    @Test
    void el_rol_se_traduce_a_una_autoridad_con_prefijo_ROLE_() throws Exception {
        // hasRole("LOCUTOR") busca internamente la autoridad "ROLE_LOCUTOR". Sin el
        // prefijo, las reglas por rol no coincidirian nunca y cualquier restriccion
        // futura por rol quedaria muda.
        Authentication auth = filtrarCon("Bearer " + jwtService.emitir(usuario()));

        assertTrue(auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_LOCUTOR")));
    }

    @Test
    void sin_cabecera_no_hay_identidad_y_la_peticion_continua() throws Exception {
        assertNull(filtrarCon(null));
    }

    @Test
    void con_otro_esquema_de_autenticacion_no_hay_identidad() throws Exception {
        assertNull(filtrarCon("Basic bG9jdXRvcjpzZWNyZXRv"));
    }

    @Test
    void con_un_token_invalido_no_hay_identidad_y_la_peticion_continua() throws Exception {
        assertNull(filtrarCon("Bearer token-que-no-vale"));
    }

    @Test
    void un_token_caducado_no_da_identidad() throws Exception {
        String caducado = new JwtService(SECRETO, -60).emitir(usuario());

        assertNull(filtrarCon("Bearer " + caducado));
    }

    @Test
    void un_token_bien_firmado_con_un_sub_que_no_es_numerico_se_descarta() throws Exception {
        // Firma valida pero contenido inesperado. Sin el control, el
        // NumberFormatException subiria como un 500 en mitad de la cadena de
        // filtros.
        assertNull(filtrarCon("Bearer " + tokenConClaims("no-es-un-numero", "x@test.com", "ADMIN")));
    }

    @Test
    void un_token_bien_firmado_sin_email_ni_rol_se_descarta() throws Exception {
        assertNull(filtrarCon("Bearer " + tokenConClaims("7", null, null)));
    }

    @Test
    void un_token_bien_firmado_sin_rol_se_descarta() throws Exception {
        // El rol es lo que se traduce a autoridad. Sin el, la identidad entraba con
        // «ROLE_null»: un rol que no existe y que ninguna regla reconoce.
        assertNull(filtrarCon("Bearer " + tokenConClaims("7", "x@test.com", null)));
    }

    @Test
    void un_token_bien_firmado_sin_email_se_descarta() throws Exception {
        // El email identifica a la persona en el chat y en los comentarios; una
        // identidad sin el no sirve para nada que haga la aplicacion.
        assertNull(filtrarCon("Bearer " + tokenConClaims("7", null, "ADMIN")));
    }

    @Test
    void si_ya_habia_identidad_en_el_contexto_el_filtro_no_la_pisa() throws Exception {
        // El filtro solo actua cuando el contexto esta vacio. Asi, si algun dia se
        // añade otro mecanismo de autenticacion antes, este no lo sobrescribe.
        Authentication previa = new org.springframework.security.authentication.UsernamePasswordAuthenticationToken(
                "ya-autenticado", null, java.util.List.of());
        SecurityContextHolder.getContext().setAuthentication(previa);

        Authentication auth = filtrarCon("Bearer " + jwtService.emitir(usuario()));

        assertEquals(previa, auth);
    }
}
