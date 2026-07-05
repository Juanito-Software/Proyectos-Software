import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import tasksRouter from './routes/tasks.js';
import authRouter from './routes/auth.js';

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.use('/api/auth', authRouter);
app.use('/api/tasks', tasksRouter);

app.get('/api/health', (req, res) => {
  res.json({ ok: true, message: 'TaskHub API' });
});

const server = app.listen(PORT, () => {
  console.log(`TaskHub API en http://localhost:${PORT}`);
});

function shutdown() {
  console.log('\nCerrando servidor…');
  server.close(() => {
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 5000);
}

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
