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
        try {
            return new UsuarioAutenticado(
                    Long.parseLong(claims.getSubject()),
                    claims.get("email", String.class),
                    claims.get("rol", String.class));
        } catch (NumberFormatException | NullPointerException ex) {
            // Token con firma valida pero contenido inesperado. Se descarta.
            return null;
        }
    }

    /** Datos del usuario que viajan en el token. */
    public record UsuarioAutenticado(Long id, String email, String rol) {
    }
}
