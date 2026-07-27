package com.radiostack.api.security;

import com.radiostack.core.domain.Usuario;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.time.Instant;
import java.util.Date;
import java.util.Optional;

/**
 * Emision y verificacion de los tokens de acceso.
 *
 * Sustituye al esquema anterior, en el que el token era la cadena
 * "Bearer-demo-" seguida del identificador del usuario. Aquel token no estaba
 * firmado, asi que cualquiera podia escribir "Bearer-demo-1" y hacerse pasar
 * por el usuario 1. No habia nada que falsificar: bastaba con teclearlo.
 *
 * Un JWT firmado con HMAC-SHA256 resuelve exactamente eso: el servidor puede
 * comprobar que el token lo emitio el, porque solo el conoce la clave. El
 * contenido del token sigue siendo legible por cualquiera (va en Base64, no
 * cifrado), de modo que NO debe llevar nada secreto: aqui solo lleva el
 * identificador, el email y el rol.
 */
@Service
public class JwtService {

    private final SecretKey clave;
    private final long duracionSegundos;

    public JwtService(
            @Value("${radiostack.jwt.secret}") String secretBase64,
            @Value("${radiostack.jwt.expiration-seconds}") long duracionSegundos) {

        byte[] bytes;
        try {
            bytes = Decoders.BASE64.decode(secretBase64);
        } catch (IllegalArgumentException ex) {
            throw new IllegalStateException(
                    "RADIOSTACK_JWT_SECRET no es Base64 valido. Genera uno con:\n"
                            + "  openssl rand -base64 48", ex);
        }

        // HMAC-SHA256 exige al menos 256 bits de clave. Una clave mas corta
        // haria el token trivial de romper por fuerza bruta, asi que se
        // rechaza al arrancar en lugar de aceptarla en silencio.
        if (bytes.length < 32) {
            throw new IllegalStateException(
                    "RADIOSTACK_JWT_SECRET es demasiado corto: " + bytes.length
                            + " bytes. Se necesitan al menos 32 (256 bits). Genera uno con:\n"
                            + "  openssl rand -base64 48");
        }

        this.clave = Keys.hmacShaKeyFor(bytes);
        this.duracionSegundos = duracionSegundos;
    }

    /** Emite un token para un usuario ya autenticado. */
    public String emitir(Usuario usuario) {
        Instant ahora = Instant.now();
        return Jwts.builder()
                .subject(String.valueOf(usuario.getId()))
                .claim("email", usuario.getEmail())
                .claim("rol", usuario.getRol().name())
                .issuedAt(Date.from(ahora))
                .expiration(Date.from(ahora.plusSeconds(duracionSegundos)))
                .signWith(clave)
                .compact();
    }

    /**
     * Verifica la firma y la caducidad del token.
     *
     * Devuelve vacio ante cualquier problema (firma invalida, token caducado,
     * formato incorrecto) en lugar de propagar la excepcion: quien llama solo
     * necesita saber si el token vale, y distinguir los motivos hacia fuera
     * ayudaria a un atacante a afinar sus intentos.
     */
    public Optional<Claims> verificar(String token) {
        try {
            return Optional.of(
                    Jwts.parser()
                            .verifyWith(clave)
                            .build()
                            .parseSignedClaims(token)
                            .getPayload());
        } catch (JwtException | IllegalArgumentException ex) {
            return Optional.empty();
        }
    }

    public long getDuracionSegundos() {
        return duracionSegundos;
    }
}
