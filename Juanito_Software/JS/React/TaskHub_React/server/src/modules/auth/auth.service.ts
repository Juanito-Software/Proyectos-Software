import { usersRepository } from '../users/users.repository.js';
import { tokenService } from './token.service.js';
import { ApiError } from '../../utils/api-error.js';
import { RegisterDTO, LoginDTO } from './auth.types.js';

export const authService = {
  async register({ username, password }: RegisterDTO) {
    const user = await usersRepository.create(username.trim(), password);
    if (!user) {
      throw ApiError.conflict('El usuario ya existe');
    }
    const token = tokenService.generateToken({ userId: user.id, username: user.username });
    return { user, token };
  },

  async login({ username, password }: LoginDTO) {
    const user = await usersRepository.findByUsername(username.trim());
    if (!user) {
      throw ApiError.unauthorized('Usuario o contraseña incorrectos');
    }
    const valid = await usersRepository.verifyPassword(user, password);
    if (!valid) {
      // Mismo mensaje que "usuario no existe": evita que un atacante use la
      // respuesta para averiguar qué nombres de usuario están registrados.
      throw ApiError.unauthorized('Usuario o contraseña incorrectos');
    }
    const token = tokenService.generateToken({ userId: user.id, username: user.username });
    return { user: usersRepository.toPublic(user), token };
  },
};
