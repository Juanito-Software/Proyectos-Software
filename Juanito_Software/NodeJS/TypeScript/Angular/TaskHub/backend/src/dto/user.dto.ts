import { Role } from '@prisma/client';

export interface UserPublicDto {
  id: string;
  name: string;
  email: string;
  role: Role;
  avatarUrl: string | null;
  createdAt: Date;
}

export interface UpdateProfileInput {
  name?: string;
  avatarUrl?: string;
}

export interface ChangePasswordInput {
  currentPassword: string;
  newPassword: string;
}
