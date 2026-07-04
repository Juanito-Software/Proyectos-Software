import bcrypt from 'bcrypt';
import { userRepository } from '../repositories/user.repository';
import { tokenService } from './token.service';
import { ApiError } from '../utils/ApiError';
import { RegisterInput, LoginInput, AuthResponseDto, AuthUserDto } from '../dto/auth.dto';

const SALT_ROUNDS = 10;

function toAuthUserDto(user: {
  id: string;
  name: string;
  email: string;
  role: import('@prisma/client').Role;
  avatarUrl: string | null;
}): AuthUserDto {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    role: user.role,
    avatarUrl: user.avatarUrl,
  };
}

export const authService = {
  async register(input: RegisterInput): Promise<AuthResponseDto> {
    const existing = await userRepository.findByEmail(input.email);
    if (existing) {
      throw ApiError.conflict('Ya existe una cuenta con ese email');
    }

    const password = await bcrypt.hash(input.password, SALT_ROUNDS);
    const user = await userRepository.create({
      name: input.name,
      email: input.email,
      password,
    });

    const accessToken = tokenService.signAccessToken(user);
    const refreshToken = await tokenService.issueRefreshToken(user.id);

    return { user: toAuthUserDto(user), accessToken, refreshToken };
  },

  async login(input: LoginInput): Promise<AuthResponseDto> {
    const user = await userRepository.findByEmail(input.email);
    if (!user) {
      throw ApiError.unauthorized('Credenciales inválidas');
    }

    const isValid = await bcrypt.compare(input.password, user.password);
    if (!isValid) {
      throw ApiError.unauthorized('Credenciales inválidas');
    }

    const accessToken = tokenService.signAccessToken(user);
    const refreshToken = await tokenService.issueRefreshToken(user.id);

    return { user: toAuthUserDto(user), accessToken, refreshToken };
  },

  async refresh(refreshToken: string) {
    const rotated = await tokenService.rotateRefreshToken(refreshToken);
    if (!rotated) {
      throw ApiError.unauthorized('Refresh token inválido o expirado');
    }
    const accessToken = tokenService.signAccessToken(rotated.user);
    return {
      user: toAuthUserDto(rotated.user),
      accessToken,
      refreshToken: rotated.refreshToken,
    };
  },

  async logout(refreshToken: string) {
    await tokenService.revokeRefreshToken(refreshToken);
  },
};
