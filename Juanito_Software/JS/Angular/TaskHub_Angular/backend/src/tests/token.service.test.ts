import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import jwt from 'jsonwebtoken';

vi.mock('../repositories/refreshToken.repository', () => ({
  refreshTokenRepository: {
    create: vi.fn(),
    findByToken: vi.fn(),
    deleteByToken: vi.fn(),
  },
}));

import { tokenService, parseExpiryToMs } from '../services/token.service';
import { refreshTokenRepository } from '../repositories/refreshToken.repository';

const repo = vi.mocked(refreshTokenRepository);

const user = { id: 'user-1', email: 'juan@test.com', role: 'MEMBER' as const };

describe('parseExpiryToMs', () => {
  it.each([
    ['30s', 30_000],
    ['15m', 900_000],
    ['2h', 7_200_000],
    ['7d', 604_800_000],
  ])('convierte %s a %i ms', (input, expected) => {
    expect(parseExpiryToMs(input)).toBe(expected);
  });

  it.each(['', 'abc', '15', 'm15', '15x', '-5m', '1.5h'])(
    'usa el fallback de 15 min para el formato inválido "%s"',
    (input) => {
      expect(parseExpiryToMs(input)).toBe(900_000);
    },
  );
});

describe('tokenService.signAccessToken', () => {
  it('firma un JWT con sub, email y role en el payload', () => {
    const token = tokenService.signAccessToken(user);
    const payload = jwt.verify(token, 'test-access-secret') as jwt.JwtPayload;

    expect(payload.sub).toBe('user-1');
    expect(payload.email).toBe('juan@test.com');
    expect(payload.role).toBe('MEMBER');
  });

  it('NO incluye la contraseña aunque venga en el objeto usuario', () => {
    const token = tokenService.signAccessToken({ ...user, password: 'hash-secreto' } as never);
    const payload = jwt.verify(token, 'test-access-secret') as jwt.JwtPayload;
    expect(payload).not.toHaveProperty('password');
  });

  it('genera un token que falla la verificación con otro secreto', () => {
    const token = tokenService.signAccessToken(user);
    expect(() => jwt.verify(token, 'secreto-incorrecto')).toThrow();
  });

  it('incluye fecha de expiración', () => {
    const token = tokenService.signAccessToken(user);
    const payload = jwt.verify(token, 'test-access-secret') as jwt.JwtPayload;
    expect(payload.exp).toBeGreaterThan(payload.iat!);
  });
});

describe('tokenService.issueRefreshToken', () => {
  beforeEach(() => vi.clearAllMocks());

  it('persiste el token con la expiración calculada y lo devuelve', async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-01-01T00:00:00Z'));

    const token = await tokenService.issueRefreshToken('user-1');

    expect(token).toMatch(/^[a-f0-9]{96}$/); // 48 bytes en hex
    expect(repo.create).toHaveBeenCalledWith(
      'user-1',
      token,
      new Date('2026-01-08T00:00:00Z'), // +7d según JWT_REFRESH_EXPIRES_IN
    );
    vi.useRealTimers();
  });

  it('genera un token distinto en cada llamada', async () => {
    const a = await tokenService.issueRefreshToken('user-1');
    const b = await tokenService.issueRefreshToken('user-1');
    expect(a).not.toBe(b);
  });
});

describe('tokenService.rotateRefreshToken', () => {
  beforeEach(() => vi.clearAllMocks());
  afterEach(() => vi.useRealTimers());

  it('devuelve null si el token no existe', async () => {
    repo.findByToken.mockResolvedValue(null as never);
    expect(await tokenService.rotateRefreshToken('inexistente')).toBeNull();
    expect(repo.deleteByToken).not.toHaveBeenCalled();
  });

  it('devuelve null y NO borra nada si el token está caducado', async () => {
    repo.findByToken.mockResolvedValue({
      userId: 'user-1',
      expiresAt: new Date('2020-01-01'),
      user,
    } as never);

    expect(await tokenService.rotateRefreshToken('caducado')).toBeNull();
    expect(repo.deleteByToken).not.toHaveBeenCalled();
  });

  it('revoca el token antiguo y emite uno nuevo cuando es válido', async () => {
    repo.findByToken.mockResolvedValue({
      userId: 'user-1',
      expiresAt: new Date(Date.now() + 86_400_000),
      user,
    } as never);

    const result = await tokenService.rotateRefreshToken('token-viejo');

    expect(repo.deleteByToken).toHaveBeenCalledWith('token-viejo');
    expect(result).not.toBeNull();
    expect(result!.refreshToken).not.toBe('token-viejo');
    expect(result!.user).toEqual(user);
  });

  it('borra el antiguo ANTES de crear el nuevo (evita tokens huérfanos)', async () => {
    const order: string[] = [];
    repo.findByToken.mockResolvedValue({
      userId: 'user-1',
      expiresAt: new Date(Date.now() + 86_400_000),
      user,
    } as never);
    repo.deleteByToken.mockImplementation(async () => {
      order.push('delete');
      return undefined as never;
    });
    repo.create.mockImplementation(async () => {
      order.push('create');
      return undefined as never;
    });

    await tokenService.rotateRefreshToken('token-viejo');
    expect(order).toEqual(['delete', 'create']);
  });
});

describe('tokenService.revokeRefreshToken', () => {
  it('delega el borrado en el repositorio', async () => {
    vi.clearAllMocks();
    await tokenService.revokeRefreshToken('abc');
    expect(repo.deleteByToken).toHaveBeenCalledWith('abc');
  });
});
