delete process.env.ADMIN_USERNAME; delete process.env.ADMIN_PASSWORD;
const { seedAdmin } = await import('./dist/config/seed-admin.js');
await seedAdmin();
console.log('  sin admin configurado -> no lanza, arranque normal');
process.env.ADMIN_USERNAME = 'x'; process.env.ADMIN_PASSWORD = 'corta';
