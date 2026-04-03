// src/main.js
// ========================================
// Telegram бот — локальный запуск Альфы
// ========================================

import express from 'express';
import dotenv from 'dotenv';
dotenv.config();

import {
  createAlphaBot,
} from './alpha-bot.js';

// ========== HTTP СЕРВЕР ДЛЯ RENDER ==========
// Render требует чтобы сервис слушал порт
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Альфа в сети! Зион на связи.');
});

app.listen(PORT, () => {
  console.log(`[Server] Port ${PORT}`);
});

// ========== ИНИЦИАЛИЗАЦИЯ БОТА ==========
const bot = createAlphaBot();


// ========== ЗАПУСК ==========
bot.launch();
console.log('[Alpha Bot] Started!');

process.once(
  'SIGINT', () => bot.stop('SIGINT')
);
process.once(
  'SIGTERM', () => bot.stop('SIGTERM')
);