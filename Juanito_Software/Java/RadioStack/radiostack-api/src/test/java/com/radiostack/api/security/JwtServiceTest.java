package com.radiostack.api.security;

import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Date;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Emision y verificacion de los tokens de acceso.
 *
 * Lo que se prueba no es que la libreria funcione, sino las decisiones de esta
 * clase: que un token solo vale si lo firmo este servidor, que caducar sirve de
 * algo, que el contenido del token no lleva nada secreto, y que una clave
 * insuficiente impide arrancar en vez de dejar pasar tokens triviales de
 * falsificar.
 */
class JwtServiceTest {

    /** 48 bytes en Base64, como pide el mensaje de ayuda del propio servicio. */
    private static final String SECRETO = Base64.getEncoder()
            .encodeToString("clave-de-prueba-de-48-bytes-para-firmar-con-hmac!".getBytes(StandardCharsets.UTF_8));

    private static final String OTRO_SECRETO = Base64.getEncoder()
            .encodeToString("otra-clave-distinta-de-48-bytes-para-firmar-hmac!".getBytes(StandardCharsets.UTF_8));

    private final JwtService servicio = new JwtService(SECRETO, 3600);

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
    void un_token_emitido_aqui_se_verifica_aqui() {
        String token = servicio.emitir(usuario());

        Optional<Claims> claims = servicio.verificar(token);

        assertTrue(claims.isPresent());
        assertEquals("7", claims.get().getSubject());
        assertEquals("locutor@radiostack.local", claims.get().get("email", String.class));
        assertEquals("LOCUTOR", claims.get().get("rol", String.class));
    }

    @Test
    void el_token_lleva_fecha_de_caducidad() {
        // Un JWT no se puede revocar: la caducidad es el unico limite real de un
        // token robado. Si se emitiera sin ella, valdria para siempre.
        Claims claims = servicio.verificar(servicio.emitir(usuario())).orElseThrow();

        assertEquals(3600, servicio.getDuracionSegundos());
        long margenMs = claims.getExpiration().getTime() - claims.getIssuedAt().getTime();
        assertEquals(3600_000L, margenMs);
    }

    @Test
    void el_contenido_del_token_no_lleva_el_hash_de_la_contrasena() {
        // El payload de un JWT va en Base64, no cifrado: cualquiera que tenga el
        // token puede leerlo. Por eso dentro solo va id, email y rol.
        String token = servicio.emitir(usuario());
        String payload = new String(
                Base64.getUrlDecoder().decode(token.split("\\.")[1]), StandardCharsets.UTF_8);

        assertFalse(payload.contains("HASH-QUE-NO-DEBE-SALIR"));
        assertFalse(payload.toLowerCase().contains("password"));
    }

    @Test
    void un_token_firmado_con_otra_clave_no_vale() {
        String ajeno = new JwtService(OTRO_SECRETO, 3600).emitir(usuario());

        assertTrue(servicio.verificar(ajeno).isEmpty());
    }

    @Test
    void un_token_caducado_no_vale() {
        // Duracion negativa: nace caducado, sin que el test tenga que esperar.
        String caducado = new JwtService(SECRETO, -60).emitir(usuario());

        assertTrue(servicio.verificar(caducado).isEmpty());
    }

    @Test
    void un_token_con_el_payload_cambiado_y_la_firma_original_no_vale() {
        String token = servicio.emitir(usuario());
        String[] partes = token.split("\\.");
        String payloadFalso = Base64.getUrlEncoder().withoutPadding().encodeToString(
                "{\"sub\":\"1\",\"email\":\"admin@radiostack.local\",\"rol\":\"ADMIN\"}"
                        .getBytes(StandardCharsets.UTF_8));

        assertTrue(servicio.verificar(partes[0] + "." + payloadFalso + "." + partes[2]).isEmpty());
    }

    @Test
    void un_token_sin_firma_no_vale() {
        // El ataque clasico contra JWT: cabecera «alg: none» y ninguna firma. Una
        // libreria mal usada lo aceptaria.
        String b64 = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0";
        String payload = Base64.getUrlEncoder().withoutPadding().encodeToString(
                "{\"sub\":\"1\",\"email\":\"admin@radiostack.local\",\"rol\":\"ADMIN\"}"
                        .getBytes(StandardCharsets.UTF_8));

        assertTrue(servicio.verificar(b64 + "." + payload + ".").isEmpty());
    }

    @Test
    void una_cadena_que_no_es_un_token_no_revienta() {
        // verificar() devuelve vacio ante cualquier problema en vez de propagar la
        // excepcion: quien llama solo necesita saber si el token vale, y distinguir
        // los motivos hacia fuera ayudaria a un atacante a afinar sus intentos.
        assertTrue(servicio.verificar("esto-no-es-un-jwt").isEmpty());
        assertTrue(servicio.verificar("").isEmpty());
    }

    @Test
    void un_token_firmado_con_la_clave_buena_pero_sin_claims_propios_se_verifica_igual() {
        // La firma es lo unico que verifica esta clase. Que el contenido tenga
        // sentido lo comprueba JwtAuthenticationFilter, y por eso este token
        // «valido pero inutil» tiene que llegar hasta alli.
        SecretKey clave = Keys.hmacShaKeyFor(Base64.getDecoder().decode(SECRETO));
        String raro = Jwts.builder()
                .subject("no-es-un-numero")
                .expiration(new Date(System.currentTimeMillis() + 60_000))
                .signWith(clave)
                .compact();

        assertTrue(servicio.verificar(raro).isPresent());
    }

    @Test
    void una_clave_de_menos_de_256_bits_impide_arrancar() {
        // HMAC-SHA256 exige 32 bytes. Con menos, el token es trivial de romper por
        // fuerza bruta, asi que el servicio se niega a construirse en lugar de
        // aceptarla en silencio.
        String corta = Base64.getEncoder().encodeToString("solo-16-bytes-ab".getBytes(StandardCharsets.UTF_8));

        IllegalStateException error = assertThrows(IllegalStateException.class, () -> new JwtService(corta, 3600));
        assertTrue(error.getMessage().contains("demasiado corto"));
    }

    @Test
    void un_secreto_que_no_es_base64_tambien_impide_arrancar() {
        // El tipo de excepcion lo decide la libreria que descodifica, asi que aqui
        // solo se fija lo que importa: que NO se construya un servicio capaz de
        // firmar con una clave que nadie ha podido descodificar.
        assertThrows(RuntimeException.class, () -> new JwtService("esto no es base64 !!", 3600));
    }
}
