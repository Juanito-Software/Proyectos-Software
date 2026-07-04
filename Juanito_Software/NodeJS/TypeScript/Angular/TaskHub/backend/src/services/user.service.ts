import bcrypt from 'bcrypt';
import { userRepository } from '../repositories/user.repository';
import { ApiError } from '../utils/ApiError';
import { ChangePasswordInput, UpdateProfileInput, UserPublicDto } from '../dto/user.dto';

function toPublicDto(user: {
  id: string;
  name: string;
  email: string;
  role: import('@prisma/client').Role;
  avatarUrl: string | null;
  createdAt: Date;
}): UserPublicDto {
  const { id, name, email, role, avatarUrl, createdAt } = user;
  return { id, name, email, role, avatarUrl, createdAt };
}

export const userService = {
  async list(page: number, limit: number) {
    const [users, total] = await Promise.all([
      userRepository.findMany({ skip: (page - 1) * limit, take: limit }),
      userRepository.count(),
    ]);
    return { data: users.map(toPublicDto), total, page, limit };
  },

  async getById(id: string) {
    const user = await userRepository.findById(id);
    if (!user) throw ApiError.notFound('Usuario no encontrado');
    return toPublicDto(user);
  },

  async updateProfile(id: string, input: UpdateProfileInput) {
    const user = await userRepository.update(id, input);
    return toPublicDto(user);
  },

  async changePassword(id: string, input: ChangePasswordInput) {
    const user = await userRepository.findById(id);
    if (!user) throw ApiError.notFound('Usuario no encontrado');

    const valid = await bcrypt.compare(input.currentPassword, user.password);
    if (!valid) throw ApiError.badRequest('La contraseña actual no es correcta');

    const hashed = await bcrypt.hash(input.newPassword, 10);
    await userRepository.update(id, { password: hashed });
  },

  async remove(id: string) {
    await userRepository.delete(id);
  },
};
