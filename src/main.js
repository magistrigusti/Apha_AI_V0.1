// src/main.js
// ========================================
// Telegram бот — Альфа, советник Зиона
// ========================================

import { Telegraf } from 'telegraf';
import { message } from 'telegraf/filters';
import dotenv from 'dotenv';
dotenv.config();

import { askAlpha } from './alpha.js';

// ========== ИНИЦИАЛИЗАЦИЯ ==========
const bot = new Telegraf(
  process.env.ALPHA_BOT_TOKEN
);

const BOT_USERNAME = 'AlphaAllod_bot';


// ========== /start ==========
bot.command('start', async (ctx) => {
  await ctx.reply(
    'Приветствую, Лорд!\n'
    + 'Я Альфа — советник Аллода Зион.\n\n'
    + 'В группе:\n'
    + '/ask <вопрос>\n'
    + 'или @' + BOT_USERNAME
    + ' <вопрос>\n\n'
    + 'В личке — просто пиши.'
  );
});


// ========== /ask ==========
bot.command('ask', async (ctx) => {
  const question = ctx.message.text
    .replace('/ask', '')
    .replace('@' + BOT_USERNAME, '')
    .trim();

  if (!question) {
    await ctx.reply(
      'Напиши вопрос после /ask\n'
      + 'Пример: /ask Что такое Аллод?'
    );
    return;
  }

  // Отправляем "Думаю…" и потом заменяем
  const wait = await ctx.reply('Думаю…');

  const answer = await askAlpha(question);

  await ctx.telegram.editMessageText(
    ctx.chat.id,
    wait.message_id,
    null,
    answer,
  );
});


// ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
bot.on(message('text'), async (ctx) => {
  const text = ctx.message.text;
  const isPrivate =
    ctx.chat.type === 'private';

  // ===== В личке — отвечаем на всё =====
  if (isPrivate) {
    const wait = await ctx.reply('Думаю…');
    const answer = await askAlpha(text);

    await ctx.telegram.editMessageText(
      ctx.chat.id,
      wait.message_id,
      null,
      answer,
    );
    return;
  }

  // ===== В группе — проверяем =====
  // Упоминание @AlphaAllod_bot
  const mentioned = text.includes(
    '@' + BOT_USERNAME
  );

  // Реплай на сообщение Альфы
  const isReply =
    ctx.message.reply_to_message
      ?.from?.id === ctx.botInfo.id;

  // Если ни то ни другое — молчим
  if (!mentioned && !isReply) return;

  // Убираем @username из текста
  const question = text
    .replace('@' + BOT_USERNAME, '')
    .trim();

  if (!question) return;

  const wait = await ctx.reply('Думаю…');
  const answer = await askAlpha(question);

  await ctx.telegram.editMessageText(
    ctx.chat.id,
    wait.message_id,
    null,
    answer,
  );
});


// ========== ЗАПУСК ==========
bot.launch();
console.log('[Alpha Bot] Started!');

process.once(
  'SIGINT', () => bot.stop('SIGINT')
);
process.once(
  'SIGTERM', () => bot.stop('SIGTERM')
);