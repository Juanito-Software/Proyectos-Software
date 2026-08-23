import fs from 'node:fs';
import crypto from 'node:crypto';
import bcrypt from 'bcrypt';
import { getUsersFile } from '../../config/paths.js';
import { User, PublicUser } from './users.types.js';

const SALT_ROUNDS = 10;

function readUsers(): User[] {
  try {
    return JSON.parse(fs.readFileSync(getUsersFile(), 'utf-8'));
  } catch {
    return [];
  }
}

function writeUsers(users: User[]): void {
  fs.writeFileSync(getUsersFile(), JSON.stringify(users, null, 2), 'utf-8');
}

function toPublic(user: User): PublicUser {
  return { id: user.id, username: user.username };
}

export const usersRepository = {
  toPublic,

  async findByUsername(username: string): Promise<User | null> {
    const users = readUsers();
    return users.find((u) => u.username.toLowerCase() === username.toLowerCase()) ?? null;
  },

  async findById(id: string): Promise<User | null> {
    const users = readUsers();
    return users.find((u) => u.id === id) ?? null;
  },

  async create(username: string, password: string): Promise<PublicUser | null> {
    const users = readUsers();
    const exists = users.some((u) => u.username.toLowerCase() === username.toLowerCase());
    if (exists) return null;

    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);
    const newUser: User = {
      id: crypto.randomUUID(),
      username: username.trim(),
      passwordHash,
      createdAt: new Date().toISOString(),
    };
    users.push(newUser);
    writeUsers(users);
    return toPublic(newUser);
  },

  async verifyPassword(user: User, password: string): Promise<boolean> {
    return bcrypt.compare(password, user.passwordHash);
  },
};
