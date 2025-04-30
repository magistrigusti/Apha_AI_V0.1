import dotenv from 'dotenv';
dotenv.config();

import { Telegraf } from 'telegraf';
import { message } from 'telegraf/filters';
import { ogg } from './ogg.js';
import { getOpenaiInstance } from './openai.js';

const openai = getOpenaiInstance(); // ← теперь переменная уже загружена

if (!process.env.BOT_TOKEN) {
  throw new Error('BOT_TOKEN не найден в .env файле!');
}

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.on(message('voice'), async ctx => {
  try {
    const link = await ctx.telegram.getFileLink(ctx.message.voice.file_id); 
    const userId = String(ctx.message.from.id);
    const oggPath = await ogg.create(link.href, userId);
    const mp3Path = await ogg.toMp3(oggPath, userId);

    const text = await openai.transcription(mp3Path);  
    await ctx.reply(text);
  } catch (e) {
    console.log(`Error while voice message`, e.message);
  }
});

bot.command('start', async (ctx) => {
  await ctx.reply(JSON.stringify(ctx.message, null, 2));
});

bot.launch();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
