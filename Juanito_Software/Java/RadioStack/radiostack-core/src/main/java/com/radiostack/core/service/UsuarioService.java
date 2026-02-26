package com.radiostack.core.service;

import com.radiostack.core.domain.Usuario;

import java.util.List;
import java.util.Optional;

public interface UsuarioService {

    Usuario registrarUsuario(Usuario usuario);

    Optional<Usuario> buscarPorEmail(String email);

    Optional<Usuario> obtenerPorId(Long id);

    List<Usuario> listarUsuarios();

    void activarUsuario(Long id);

    void desactivarUsuario(Long id);
}

