import { z } from 'zod';

export const createProjectSchema = z.object({
  body: z.object({
    name: z.string().trim().min(2, 'El nombre debe tener al menos 2 caracteres'),
    description: z.string().trim().max(1000).optional(),
  }),
});

export const updateProjectSchema = z.object({
  body: z.object({
    name: z.string().trim().min(2).optional(),
    description: z.string().trim().max(1000).optional(),
  }),
});

export const addMemberSchema = z.object({
  body: z.object({
    // Por email y no por id: la pantalla no lista a los usuarios registrados,
    // el propietario escribe el email de quien quiere añadir. Se recorta pero no
    // se pasa a minusculas, igual que en el registro y el login: si no, un email
    // guardado con mayusculas dejaria de encontrarse.
    email: z.string().trim().email('Email inválido'),
    // OWNER no es asignable: el propietario es uno solo (`ownerId`), y un
    // segundo «OWNER» tendria los permisos de un EDITOR con otro nombre.
    role: z.enum(['EDITOR', 'VIEWER']).optional(),
  }),
});
