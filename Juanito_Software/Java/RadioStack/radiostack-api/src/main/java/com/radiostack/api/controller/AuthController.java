package com.radiostack.api.controller;

import com.radiostack.api.dto.AuthDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.service.UsuarioService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final UsuarioService usuarioService;
    private final PasswordEncoder passwordEncoder;

    public AuthController(UsuarioService usuarioService, PasswordEncoder passwordEncoder) {
        this.usuarioService = usuarioService;
        this.passwordEncoder = passwordEncoder;
    }

    @PostMapping("/login")
    public ResponseEntity<AuthDTO.LoginResponse> login(@RequestBody AuthDTO.LoginRequest request) {
        return usuarioService.buscarPorEmail(request.getEmail())
                .filter(u -> passwordEncoder.matches(request.getPassword(), u.getPasswordHash()))
                .filter(u -> u.isActivo())
                .map(u -> {
                    AuthDTO.LoginResponse res = new AuthDTO.LoginResponse();
                    res.setToken("Bearer-demo-" + u.getId());
                    res.setUsuario(DtoMapper.toUsuarioDTO(u));
                    return ResponseEntity.ok(res);
                })
                .orElse(ResponseEntity.status(401).build());
    }

    @GetMapping("/me")
    public ResponseEntity<AuthDTO.LoginResponse> me(@RequestHeader(value = "Authorization", required = false) String auth) {
        if (auth == null || !auth.startsWith("Bearer-demo-")) {
            return ResponseEntity.status(401).build();
        }
        try {
            Long id = Long.parseLong(auth.replace("Bearer-demo-", ""));
            return usuarioService.obtenerPorId(id)
                    .map(u -> {
                        AuthDTO.LoginResponse res = new AuthDTO.LoginResponse();
                        res.setToken(auth);
                        res.setUsuario(DtoMapper.toUsuarioDTO(u));
                        return ResponseEntity.<AuthDTO.LoginResponse>ok(res);
                    })
                    .orElse(ResponseEntity.status(401).build());
        } catch (NumberFormatException e) {
            return ResponseEntity.status(401).build();
        }
    }
}
