import express from 'express';
import * as storeUsers from '../storeUsers.js';
import { generateToken } from '../middleware/auth.js';
import { authLimiter } from '../middleware/rateLimit.js';

const router = express.Router();

// Límite de intentos en todas las rutas de este router: son las que permiten
// adivinar credenciales por fuerza bruta.
router.use(authLimiter);

// POST /api/auth/register
router.post('/register', async (req, res) => {
  const { username, password } = req.body;
  if (!username?.trim() || !password) {
    return res.status(400).json({ error: 'Usuario y contraseña son obligatorios' });
  }
  if (password.length < 6) {
    return res.status(400).json({ error: 'La contraseña debe tener al menos 6 caracteres' });
  }
  const user = await storeUsers.createUser(username.trim(), password);
  if (!user) {
    return res.status(409).json({ error: 'El usuario ya existe' });
  }
  const token = generateToken(user);
  res.status(201).json({ user: { id: user.id, username: user.username }, token });
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { username, password } = req.body;
  if (!username?.trim() || !password) {
    return res.status(400).json({ error: 'Usuario y contraseña son obligatorios' });
  }
  const user = await storeUsers.findUserByUsername(username.trim());
  if (!user) {
    return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
  }
  const valid = await storeUsers.verifyPassword(user, password);
  if (!valid) {
    return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
  }
  const token = generateToken({ id: user.id, username: user.username });
  res.json({ user: { id: user.id, username: user.username }, token });
});

export default router;
