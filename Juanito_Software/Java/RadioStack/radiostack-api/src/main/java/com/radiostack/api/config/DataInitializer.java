package com.radiostack.api.config;

import com.radiostack.core.domain.RolUsuario;
import com.radiostack.core.domain.Usuario;
import com.radiostack.core.service.UsuarioService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class DataInitializer {

    @Bean
    public CommandLineRunner initAdmin(UsuarioService usuarioService, PasswordEncoder passwordEncoder) {
        return args -> {
            if (usuarioService.buscarPorEmail("admin@radiostack.local").isEmpty()) {
                Usuario admin = new Usuario();
                admin.setNombre("Admin");
                admin.setEmail("admin@radiostack.local");
                admin.setPasswordHash(passwordEncoder.encode("admin123"));
                admin.setRol(RolUsuario.ADMIN);
                admin.setActivo(true);
                usuarioService.registrarUsuario(admin);
            }
        };
    }
}
