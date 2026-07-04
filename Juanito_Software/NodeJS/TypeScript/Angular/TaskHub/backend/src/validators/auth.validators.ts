import { z } from 'zod';

export const registerSchema = z.object({
  body: z.object({
    name: z.string().trim().min(2, 'El nombre debe tener al menos 2 caracteres'),
    email: z.string().trim().email('Email inválido'),
    password: z
      .string()
      .min(8, 'La contraseña debe tener al menos 8 caracteres')
      .regex(/[A-Z]/, 'Debe incluir al menos una mayúscula')
      .regex(/[0-9]/, 'Debe incluir al menos un número'),
  }),
});

export const loginSchema = z.object({
  body: z.object({
    email: z.string().trim().email('Email inválido'),
    password: z.string().min(1, 'La contraseña es obligatoria'),
  }),
});

export type RegisterSchema = z.infer<typeof registerSchema>['body'];
export type LoginSchema = z.infer<typeof loginSchema>['body'];
