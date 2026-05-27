import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_FILE = path.join(__dirname, 'data', 'tasks.json');

function readTasks() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(data);
  } catch {
    return [];
  }
}

function writeTasks(tasks) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(tasks, null, 2), 'utf-8');
}

export function getAllTasks() {
  return readTasks();
}

export function getTaskById(id, userId) {
  const tasks = readTasks();
  const task = tasks.find((t) => t.id === id);
  return task?.userId === userId ? task : null;
}

export function getAllTasksByUser(userId) {
  const tasks = readTasks();
  return tasks.filter((t) => t.userId === userId);
}

export function createTask(task, userId) {
  const tasks = readTasks();
  const newTask = {
    id: crypto.randomUUID(),
    title: task.title || '',
    description: task.description || '',
    completed: task.completed ?? false,
    userId: userId,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  tasks.push(newTask);
  writeTasks(tasks);
  return newTask;
}

export function updateTask(id, userId, updates) {
  const tasks = readTasks();
  const index = tasks.findIndex((t) => t.id === id && t.userId === userId);
  if (index === -1) return null;
  tasks[index] = {
    ...tasks[index],
    ...updates,
    updatedAt: new Date().toISOString(),
  };
  writeTasks(tasks);
  return tasks[index];
}

export function deleteTask(id, userId) {
  const tasks = readTasks();
  const index = tasks.findIndex((t) => t.id === id && t.userId === userId);
  if (index === -1) return false;
  tasks.splice(index, 1);
  writeTasks(tasks);
  return true;
}
