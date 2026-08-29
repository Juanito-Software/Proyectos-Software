const { createApp } = await import('./dist/app.js');
const s = createApp().listen(4099);
const get = async (p) => {
  const r = await fetch('http://localhost:4099' + p, { redirect: 'manual' });
  const t = await r.text();
  const kind = t.startsWith('{') ? 'JSON' : t.includes('Playground') ? 'PLAYGROUND' : t.includes('<!DOCTYPE') ? 'HTML cliente' : '?';
  console.log(`  ${p.padEnd(26)} -> ${r.status}  ${kind}`);
};
await get('/');
await get('/playground');
await get('/login');
await get('/api/health');
await get('/api/no-existe');
s.close();
