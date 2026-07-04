import { PrismaClient, Role } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  const passwordHash = await bcrypt.hash('Password123!', 10);

  const admin = await prisma.user.upsert({
    where: { email: 'admin@taskmanager.dev' },
    update: {},
    create: {
      name: 'Admin',
      email: 'admin@taskmanager.dev',
      password: passwordHash,
      role: Role.ADMIN,
    },
  });

  const project = await prisma.project.upsert({
    where: { id: 'seed-project-1' },
    update: {},
    create: {
      id: 'seed-project-1',
      name: 'Proyecto de ejemplo',
      description: 'Proyecto creado por el seed inicial',
      ownerId: admin.id,
      members: {
        create: { userId: admin.id, role: 'OWNER' },
      },
    },
  });

  await prisma.task.create({
    data: {
      title: 'Configurar el proyecto',
      description: 'Tarea de ejemplo generada por el seed',
      projectId: project.id,
      creatorId: admin.id,
      assigneeId: admin.id,
    },
  });

  console.log('Seed completado. Usuario admin: admin@taskmanager.dev / Password123!');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
