import { Telegraf } from 'telegraf';
import dotenv from 'dotenv';

if (!process.env.BOT_TOKEN) {
  throw new Error('BOT_TOKEN не найден в .env файле!');
}

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.launch();

process.once('SICINT', () => bot.stop('SIGINT'));
process.once('SICTERM', () => bot.stop('SIGTERM'));