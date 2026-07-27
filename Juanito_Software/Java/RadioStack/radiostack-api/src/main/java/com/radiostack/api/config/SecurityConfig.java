package com.radiostack.api.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {

        http
            // CSRF desactivado a proposito, no por descuido.
            //
            // Un ataque CSRF necesita que el navegador adjunte credenciales por
            // su cuenta a una peticion provocada desde otro sitio web: una
            // cookie de sesion que viaja sola. Esta API es STATELESS y no crea
            // ninguna sesion ni emite ninguna cookie, asi que una peticion
            // forjada llega sin identidad, igual que la de cualquier
            // desconocido. No hay nada que suplantar.
            //
            // Si algun dia se anade autenticacion por sesion o por cookie, hay
            // que volver a activar CSRF.
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .anyRequest().permitAll()
            );

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}