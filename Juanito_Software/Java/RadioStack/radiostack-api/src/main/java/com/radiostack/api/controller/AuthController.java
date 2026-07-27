package com.radiostack.api.controller;

import com.radiostack.api.dto.AuthDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.api.security.JwtAuthenticationFilter.UsuarioAutenticado;
import com.radiostack.api.security.JwtService;
import com.radiostack.core.service.UsuarioService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final UsuarioService usuarioService;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthController(UsuarioService usuarioService,
                          PasswordEncoder passwordEncoder,
                          JwtService jwtService) {
        this.usuarioService = usuarioService;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    /**
     * Comprueba las credenciales y devuelve un token firmado.
     *
     * El token que se devuelve es el JWT pelado, sin el prefijo "Bearer ".
     * Ese prefijo pertenece a la cabecera HTTP, no al token, y lo anade el
     * cliente al enviarlo. Antes iba incrustado en la propia cadena
     * ("Bearer-demo-<id>"), lo que mezclaba las dos cosas.
     */
    @PostMapping("/login")
    public ResponseEntity<AuthDTO.LoginResponse> login(@RequestBody AuthDTO.LoginRequest request) {
        return usuarioService.buscarPorEmail(request.getEmail())
                .filter(u -> passwordEncoder.matches(request.getPassword(), u.getPasswordHash()))
                .filter(u -> u.isActivo())
                .map(u -> {
                    AuthDTO.LoginResponse res = new AuthDTO.LoginResponse();
                    res.setToken(jwtService.emitir(u));
                    res.setUsuario(DtoMapper.toUsuarioDTO(u));
                    return ResponseEntity.ok(res);
                })
                .orElse(ResponseEntity.status(401).build());
    }

    /**
     * Devuelve el usuario correspondiente al token recibido.
     *
     * Ya no se interpreta la cabecera aqui: cuando este metodo se ejecuta, el
     * filtro JWT ya ha comprobado la firma y la caducidad, y SecurityConfig ya
     * ha exigido que la peticion venga autenticada. Este controlador solo
     * traduce el usuario del token a su representacion actual en base de datos.
     */
    @GetMapping("/me")
    public ResponseEntity<AuthDTO.LoginResponse> me(@AuthenticationPrincipal UsuarioAutenticado autenticado) {
        if (autenticado == null) {
            return ResponseEntity.status(401).build();
        }
        return usuarioService.obtenerPorId(autenticado.id())
                // Un token puede seguir siendo valido despues de que la cuenta
                // se desactive, porque los JWT no se pueden revocar. Se
                // comprueba aqui contra la base de datos.
                .filter(u -> u.isActivo())
                .map(u -> {
                    AuthDTO.LoginResponse res = new AuthDTO.LoginResponse();
                    res.setUsuario(DtoMapper.toUsuarioDTO(u));
                    return ResponseEntity.ok(res);
                })
                .orElse(ResponseEntity.status(401).build());
    }
}
