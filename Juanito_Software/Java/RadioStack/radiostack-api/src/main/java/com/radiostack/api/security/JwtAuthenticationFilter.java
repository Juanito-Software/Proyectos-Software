package com.radiostack.api.security;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

/**
 * Lee el token de la cabecera Authorization y, si es valido, deja al usuario
 * autenticado en el contexto de seguridad para el resto de la peticion.
 *
 * El filtro nunca rechaza una peticion por si mismo: si no hay token o el
 * token no vale, simplemente deja el contexto vacio y sigue. Es
 * SecurityConfig quien decide despues si esa ruta exige o no autenticacion.
 * Separar ambas cosas evita tener las reglas de acceso repartidas en dos
 * sitios.
 */
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String CABECERA = "Authorization";
    private static final String PREFIJO = "Bearer ";

    private final JwtService jwtService;

    public JwtAuthenticationFilter(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain chain) throws ServletException, IOException {

        String cabecera = request.getHeader(CABECERA);

        if (cabecera != null && cabecera.startsWith(PREFIJO)
                && SecurityContextHolder.getContext().getAuthentication() == null) {

            String token = cabecera.substring(PREFIJO.length()).trim();

            jwtService.verificar(token).ifPresent(claims -> {
                UsuarioAutenticado usuario = aUsuario(claims);
                if (usuario != null) {
                    // El prefijo ROLE_ es una convencion de Spring Security:
                    // hasRole("ADMIN") busca internamente la autoridad
                    // "ROLE_ADMIN". Sin el prefijo, las reglas por rol no
                    // llegarian a coincidir nunca.
                    var auth = new UsernamePasswordAuthenticationToken(
                            usuario,
                            null,
                            List.of(new SimpleGrantedAuthority("ROLE_" + usuario.rol())));
                    auth.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(auth);
                }
            });
        }

        chain.doFilter(request, response);
    }

    private UsuarioAutenticado aUsuario(Claims claims) {
        return UsuarioAutenticado.desde(claims).orElse(null);
    }

    /** Datos del usuario que viajan en el token. */
    public record UsuarioAutenticado(Long id, String email, String rol) {

        /**
         * Traduce los claims de un token YA verificado, o vacio si su contenido no
         * sirve: sin `sub` numerico, sin email o sin rol.
         *
         * La version anterior solo se protegia del `sub`, con un catch de
         * NullPointerException que nunca se ejecutaba: `claims.get(...)` devuelve
         * null en lugar de lanzar, y un record acepta nulos sin protestar. Un token
         * firmado pero sin claims autenticaba con email y rol a null y la autoridad
         * literal «ROLE_null»: una identidad a medias que ninguna regla por rol
         * reconoceria y que en el chat habria firmado los mensajes como «null».
         * Solo el servidor puede firmar, asi que no era explotable desde fuera; era
         * una defensa escrita que no defendia.
         *
         * Lo usan el filtro HTTP y el interceptor de STOMP, para que las dos puertas
         * acepten exactamente los mismos tokens.
         */
        public static Optional<UsuarioAutenticado> desde(Claims claims) {
            String email = claims.get("email", String.class);
            String rol = claims.get("rol", String.class);
            if (email == null || email.isBlank() || rol == null || rol.isBlank()) {
                return Optional.empty();
            }
            try {
                return Optional.of(new UsuarioAutenticado(Long.parseLong(claims.getSubject()), email, rol));
            } catch (NumberFormatException ex) {
                // Incluye el caso de un token sin `sub`: parseLong(null) lanza aqui.
                return Optional.empty();
            }
        }
    }
}
