import dotenv from 'dotenv';
import app from './app';

// Load environment variables from .env file
dotenv.config();

const PORT = process.env.PORT || 3000;

const server = app.listen(PORT, () => {
  console.log('==================================================');
  console.log(`🚀 Server running in ${process.env.NODE_ENV || 'development'} mode`);
  console.log(`🔌 Listening on http://localhost:${PORT}`);
  console.log(`🌐 API Playground available at: http://localhost:${PORT}`);
  console.log('==================================================');
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('⚠️ SIGTERM received. Shutting down gracefully...');
  server.close(() => {
    console.log('🛑 Server closed.');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('⚠️ SIGINT received. Shutting down gracefully...');
  server.close(() => {
    console.log('🛑 Server closed.');
    process.exit(0);
  });
});
