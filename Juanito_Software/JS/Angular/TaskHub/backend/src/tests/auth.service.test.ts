import { describe, it, expect, vi, beforeEach } from 'vitest';
import bcrypt from 'bcrypt';

vi.mock('../repositories/user.repository', () => ({
  userRepository: { findByEmail: vi.fn(), create: vi.fn() },
}));

vi.mock('../services/token.service', () => ({
  tokenService: {
    signAccessToken: vi.fn(() => 'access-token-fake'),
    issueRefreshToken: vi.fn(async () => 'refresh-token-fake'),
    rotateRefreshToken: vi.fn(),
    revokeRefreshToken: vi.fn(),
  },
}));

import { authService } from '../services/auth.service';
import { userRepository } from '../repositories/user.repository';
import { tokenService } from '../services/token.service';
import { ApiError } from '../utils/ApiError';

const users = vi.mocked(userRepository);
const tokens = vi.mocked(tokenService);

const storedUser = {
  id: 'user-1',
  name: 'Juan',
  email: 'juan@test.com',
  password: '$2b$10$hashFalso',
  role: 'MEMBER' as const,
  avatarUrl: null,
  createdAt: new Date('2026-01-01'),
  updatedAt: new Date('2026-01-01'),
};

beforeEach(() => {
  vi.clearAllMocks();
  tokens.signAccessToken.mockReturnValue('access-token-fake');
  tokens.issueRefreshToken.mockResolvedValue('refresh-token-fake');
});

describe('authService.register', () => {
  const input = { name: 'Juan', email: 'juan@test.com', password: 'secreto123' };

  it('lanza 409 si el email ya está registrado', async () => {
    users.findByEmail.mockResolvedValue(storedUser as never);

    await expect(authService.register(input)).rejects.toThrowError(ApiError);
    await expect(authService.register(input)).rejects.toMatchObject({ statusCode: 409 });
    expect(users.create).not.toHaveBeenCalled();
  });

  it('hashea la contraseña antes de persistirla (nunca en claro)', async () => {
    users.findByEmail.mockResolvedValue(null as never);
    users.create.mockResolvedValue(storedUser as never);

    await authService.register(input);

    const persisted = users.create.mock.calls[0][0] as { password: string };
    expect(persisted.password).not.toBe('secreto123');
    expect(persisted.password).toMatch(/^\$2[aby]\$/); // formato bcrypt
    expect(await bcrypt.compare('secreto123', persisted.password)).toBe(true);
  });

  it('devuelve usuario público + ambos tokens, sin exponer el hash', async () => {
    users.findByEmail.mockResolvedValue(null as never);
    users.create.mockResolvedValue(storedUser as never);

    const result = await authService.register(input);

    expect(result.user).toEqual({
      id: 'user-1',
      name: 'Juan',
      email: 'juan@test.com',
      role: 'MEMBER',
      avatarUrl: null,
    });
    expect(result.user).not.toHaveProperty('password');
    expect(result.accessToken).toBe('access-token-fake');
    expect(result.refreshToken).toBe('refresh-token-fake');
  });
});

describe('authService.login', () => {
  const input = { email: 'juan@test.com', password: 'secreto123' };

  it('lanza 401 si el usuario no existe', async () => {
    users.findByEmail.mockResolvedValue(null as never);
    await expect(authService.login(input)).rejects.toMatchObject({ statusCode: 401 });
  });

  it('lanza 401 si la contraseña no coincide', async () => {
    users.findByEmail.mockResolvedValue({
      ...storedUser,
      password: await bcrypt.hash('otra-password', 10),
    } as never);

    await expect(authService.login(input)).rejects.toMatchObject({ statusCode: 401 });
    expect(tokens.issueRefreshToken).not.toHaveBeenCalled();
  });

  it('usa el MISMO mensaje para usuario inexistente y password incorrecta', async () => {
    // Evita enumeración de usuarios: un atacante no debe distinguir ambos casos.
    users.findByEmail.mockResolvedValue(null as never);
    const noUser = await authService.login(input).catch((e: ApiError) => e.message);

    users.findByEmail.mockResolvedValue({
      ...storedUser,
      password: await bcrypt.hash('otra', 10),
    } as never);
    const badPass = await authService.login(input).catch((e: ApiError) => e.message);

    expect(noUser).toBe(badPass);
  });

  it('emite tokens cuando las credenciales son correctas', async () => {
    users.findByEmail.mockResolvedValue({
      ...storedUser,
      password: await bcrypt.hash('secreto123', 10),
    } as never);

    const result = await authService.login(input);

    expect(result.accessToken).toBe('access-token-fake');
    expect(result.refreshToken).toBe('refresh-token-fake');
    expect(tokens.issueRefreshToken).toHaveBeenCalledWith('user-1');
  });
});

describe('authService.refresh', () => {
  it('lanza 401 si la rotación devuelve null', async () => {
    tokens.rotateRefreshToken.mockResolvedValue(null as never);
    await expect(authService.refresh('malo')).rejects.toMatchObject({ statusCode: 401 });
  });

  it('devuelve nuevo access token y el refresh rotado', async () => {
    tokens.rotateRefreshToken.mockResolvedValue({
      user: storedUser,
      refreshToken: 'refresh-rotado',
    } as never);

    const result = await authService.refresh('token-viejo');

    expect(result.refreshToken).toBe('refresh-rotado');
    expect(result.accessToken).toBe('access-token-fake');
    expect(result.user).not.toHaveProperty('password');
  });
});

describe('authService.logout', () => {
  it('revoca el refresh token recibido', async () => {
    await authService.logout('token-a-revocar');
    expect(tokens.revokeRefreshToken).toHaveBeenCalledWith('token-a-revocar');
  });
});
