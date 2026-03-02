import express from 'express';
import * as store from '../store.js';
import { authMiddleware } from '../middleware/auth.js';

const router = express.Router();

router.use(authMiddleware);

// GET /api/tasks - Listar tareas del usuario autenticado
router.get('/', (req, res) => {
  const tasks = store.getAllTasksByUser(req.userId);
  res.json(tasks);
});

// GET /api/tasks/:id - Obtener una tarea por ID
router.get('/:id', (req, res) => {
  const task = store.getTaskById(req.params.id, req.userId);
  if (!task) return res.status(404).json({ error: 'Tarea no encontrada' });
  res.json(task);
});

// POST /api/tasks - Crear tarea
router.post('/', (req, res) => {
  const { title, description, completed } = req.body;
  if (!title?.trim()) {
    return res.status(400).json({ error: 'El título es obligatorio' });
  }
  const task = store.createTask(
    { title: title.trim(), description: description?.trim() ?? '', completed: !!completed },
    req.userId
  );
  res.status(201).json(task);
});

// PUT /api/tasks/:id - Actualizar tarea completa
router.put('/:id', (req, res) => {
  const task = store.getTaskById(req.params.id, req.userId);
  if (!task) return res.status(404).json({ error: 'Tarea no encontrada' });
  const { title, description, completed } = req.body;
  const updated = store.updateTask(req.params.id, req.userId, {
    title: title !== undefined ? String(title).trim() : task.title,
    description: description !== undefined ? String(description).trim() : task.description,
    completed: completed !== undefined ? !!completed : task.completed,
  });
  res.json(updated);
});

// PATCH /api/tasks/:id - Actualización parcial (ej. solo marcar completada)
router.patch('/:id', (req, res) => {
  const task = store.getTaskById(req.params.id, req.userId);
  if (!task) return res.status(404).json({ error: 'Tarea no encontrada' });
  const updates = {};
  if (req.body.title !== undefined) updates.title = String(req.body.title).trim();
  if (req.body.description !== undefined) updates.description = String(req.body.description).trim();
  if (req.body.completed !== undefined) updates.completed = !!req.body.completed;
  const updated = store.updateTask(req.params.id, req.userId, updates);
  res.json(updated);
});

// DELETE /api/tasks/:id - Eliminar tarea
router.delete('/:id', (req, res) => {
  const deleted = store.deleteTask(req.params.id, req.userId);
  if (!deleted) return res.status(404).json({ error: 'Tarea no encontrada' });
  res.status(204).send();
});

export default router;
