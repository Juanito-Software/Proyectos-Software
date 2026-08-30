import { createApp } from './src/app.js';
console.log('  NODE_ENV=' + (process.env.NODE_ENV ?? 'development') + ' -> trust proxy:', createApp().get('trust proxy'));
