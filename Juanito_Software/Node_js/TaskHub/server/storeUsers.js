import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import bcrypt from 'bcrypt';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_FILE = path.join(__dirname, 'data', 'users.json');

function readUsers() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return [];
  }
}

function writeUsers(users) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(users, null, 2), 'utf-8');
}

export async function findUserByUsername(username) {
  const users = readUsers();
  return users.find((u) => u.username.toLowerCase() === username.toLowerCase()) ?? null;
}

export async function findUserById(id) {
  const users = readUsers();
  return users.find((u) => u.id === id) ?? null;
}

export async function createUser(username, password) {
  const users = readUsers();
  const exists = users.some((u) => u.username.toLowerCase() === username.toLowerCase());
  if (exists) return null;

  const passwordHash = await bcrypt.hash(password, 10);
  const newUser = {
    id: crypto.randomUUID(),
    username: username.trim(),
    passwordHash,
    createdAt: new Date().toISOString(),
  };
  users.push(newUser);
  writeUsers(users);
  return { id: newUser.id, username: newUser.username };
}

export async function verifyPassword(user, password) {
  return bcrypt.compare(password, user.passwordHash);
}
