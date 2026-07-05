import { Role } from '@prisma/client';

export interface RegisterInput {
  name: string;
  email: string;
  password: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface AuthUserDto {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatarUrl: string | null;
}

export interface AuthResponseDto {
  user: AuthUserDto;
  accessToken: string;
  refreshToken: string;
}
