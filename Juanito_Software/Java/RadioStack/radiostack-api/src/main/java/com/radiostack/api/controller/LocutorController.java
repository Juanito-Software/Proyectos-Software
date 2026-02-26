package com.radiostack.api.controller;

import com.radiostack.api.dto.LocutorDTO;
import com.radiostack.api.mapper.DtoMapper;
import com.radiostack.core.domain.Locutor;
import com.radiostack.core.domain.Usuario;
import com.radiostack.core.port.LocutorRepository;
import com.radiostack.core.port.UsuarioRepository;
import com.radiostack.core.service.UsuarioService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/locutores")
public class LocutorController {

    private final LocutorRepository locutorRepository;
    private final UsuarioRepository usuarioRepository;
    private final UsuarioService usuarioService;
    private final PasswordEncoder passwordEncoder;

    public LocutorController(LocutorRepository locutorRepository,
                             UsuarioRepository usuarioRepository,
                             UsuarioService usuarioService,
                             PasswordEncoder passwordEncoder) {
        this.locutorRepository = locutorRepository;
        this.usuarioRepository = usuarioRepository;
        this.usuarioService = usuarioService;
        this.passwordEncoder = passwordEncoder;
    }

    @GetMapping
    public List<LocutorDTO> listar() {
        return locutorRepository.findAll().stream()
                .map(DtoMapper::toLocutorDTO)
                .toList();
    }

    @PostMapping
    public ResponseEntity<LocutorDTO> crear(@RequestBody LocutorDTO dto) {
        Usuario u = new Usuario();
        u.setNombre(dto.getUsuarioNombre() != null ? dto.getUsuarioNombre() : "Locutor");
        u.setEmail(dto.getUsuarioEmail());
        u.setPasswordHash(passwordEncoder.encode("cambiar123"));
        u.setRol(com.radiostack.core.domain.RolUsuario.LOCUTOR);
        u.setActivo(true);
        u = usuarioService.registrarUsuario(u);
        Locutor l = new Locutor();
        l.setNombreArtistico(dto.getNombreArtistico() != null ? dto.getNombreArtistico() : u.getNombre());
        l.setUsuario(u);
        Locutor creado = locutorRepository.save(l);
        return ResponseEntity.status(HttpStatus.CREATED).body(DtoMapper.toLocutorDTO(creado));
    }

    @PatchMapping("/{id}/activar")
    public ResponseEntity<LocutorDTO> activar(@PathVariable Long id) {
        Locutor l = locutorRepository.findById(id).orElse(null);
        if (l == null || l.getUsuario() == null) return ResponseEntity.notFound().build();
        usuarioService.activarUsuario(l.getUsuario().getId());
        return ResponseEntity.ok(DtoMapper.toLocutorDTO(locutorRepository.findById(id).orElse(l)));
    }

    @PatchMapping("/{id}/desactivar")
    public ResponseEntity<LocutorDTO> desactivar(@PathVariable Long id) {
        Locutor l = locutorRepository.findById(id).orElse(null);
        if (l == null || l.getUsuario() == null) return ResponseEntity.notFound().build();
        usuarioService.desactivarUsuario(l.getUsuario().getId());
        return ResponseEntity.ok(DtoMapper.toLocutorDTO(locutorRepository.findById(id).orElse(l)));
    }
}
