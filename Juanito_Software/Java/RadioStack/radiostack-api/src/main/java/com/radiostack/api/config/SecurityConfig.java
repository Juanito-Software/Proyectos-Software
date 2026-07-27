package com.radiostack.api.config;

import com.radiostack.api.security.JwtAuthenticationFilter;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

        http
            // CSRF desactivado a proposito, no por descuido.
            //
            // Un ataque CSRF necesita que el navegador adjunte credenciales por
            // su cuenta a una peticion provocada desde otro sitio web: una
            // cookie de sesion que viaja sola. Esta API es STATELESS, no crea
            // sesion y no emite ninguna cookie; se autentica con un token en la
            // cabecera Authorization, que el navegador no anade solo. Una
            // peticion forjada llega sin identidad.
            //
            // Si algun dia se anade autenticacion por sesion o por cookie, hay
            // que volver a activar CSRF.
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                // Iniciar sesion tiene que ser accesible sin haber iniciado sesion.
                .requestMatchers(HttpMethod.POST, "/api/v1/auth/login").permitAll()

                // Documentacion y comprobacion de vida.
                .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
                .requestMatchers("/actuator/health").permitAll()

                // El handshake del WebSocket se deja pasar aqui porque no puede
                // llevar cabecera Authorization: no hay nada que validar en
                // este punto. La autenticacion del chat ocurre una trama
                // despues, en el CONNECT de STOMP, y la hace
                // StompAuthChannelInterceptor. Leer es publico, escribir exige
                // token, igual que en HTTP.
                .requestMatchers("/ws/**").permitAll()

                // Consultas publicas: la parrilla, los programas y las emisiones
                // de una radio son informacion destinada a los oyentes. Se deja
                // abierta la lectura y se protege todo lo que modifica datos.
                .requestMatchers(HttpMethod.GET, "/api/v1/**").permitAll()

                // El resto (POST, PUT, PATCH, DELETE) exige token valido.
                .anyRequest().authenticated()
            )
            // El filtro se coloca antes del de usuario y contrasena porque para
            // cuando Spring llegue a decidir si la peticion esta autorizada, la
            // identidad ya tiene que estar puesta en el contexto.
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
            .exceptionHandling(ex -> ex
                // Sin esto, una peticion sin token recibiria 403. El codigo
                // correcto es 401: no es que no tengas permiso, es que no has
                // dicho quien eres.
                .authenticationEntryPoint((req, res, e) ->
                    res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Se requiere autenticacion"))
            );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
