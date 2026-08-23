import jwt from 'jsonwebtoken';
import crypto from 'node:crypto';
import { env } from '../config/env';
import { User } from '@prisma/client';
import { refreshTokenRepository } from '../repositories/refreshToken.repository';

export function parseExpiryToMs(value: string): number {
  const match = /^(\d+)([smhd])$/.exec(value);
  if (!match) return 15 * 60 * 1000; // fallback: 15 min
  const amount = Number(match[1]);
  const unit = match[2];
  const unitMs = { s: 1000, m: 60_000, h: 3_600_000, d: 86_400_000 }[unit] ?? 60_000;
  return amount * unitMs;
}

export const tokenService = {
  signAccessToken(user: Pick<User, 'id' | 'email' | 'role'>) {
    return jwt.sign({ sub: user.id, email: user.email, role: user.role }, env.jwt.secret, {
      expiresIn: env.jwt.expiresIn as jwt.SignOptions['expiresIn'],
    });
  },

  async issueRefreshToken(userId: string) {
    const token = crypto.randomBytes(48).toString('hex');
    const expiresAt = new Date(Date.now() + parseExpiryToMs(env.jwt.refreshExpiresIn));
    await refreshTokenRepository.create(userId, token, expiresAt);
    return token;
  },

  async rotateRefreshToken(oldToken: string) {
    const stored = await refreshTokenRepository.findByToken(oldToken);
    if (!stored || stored.expiresAt < new Date()) {
      return null;
    }
    await refreshTokenRepository.deleteByToken(oldToken);
    const newToken = await this.issueRefreshToken(stored.userId);
    return { user: stored.user, refreshToken: newToken };
  },

  revokeRefreshToken(token: string) {
    return refreshTokenRepository.deleteByToken(token);
  },
};
