import { Telegraf } from 'telegraf';
import { message } from 'telegraf/filters';
import dotenv from 'dotenv';
dotenv.config();

import { ogg } from './ogg.js';
import { openai } from './openai.js';
import { code } from 'telegraf/format';

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.on(message('voice'), async ctx => {
  try {
    await ctx.reply('🛰 Сообщение получено. Жду ответ от сервера…');

    const link = await ctx.telegram.getFileLink(ctx.message.voice.file_id);
    const userId = String(ctx.message.from.id);

    const oggPath = await ogg.create(link.href, userId);
    const mp3Path = await ogg.toMp3(oggPath, userId);

    console.log('MP3 path:', mp3Path); // debug

    const text = await openai.transcription(mp3Path);
    console.log('Transcribed text:', text);

    const response = await openai.chat(text);
    console.log('GPT response:', response);

    await ctx.reply(response);
  } catch (e) {
    console.error('Ошибка обработки голосового:', e.message);
    await ctx.reply('❌ Ошибка при обработке. Попробуй ещё раз.');
  }
});

bot.command('start', async (ctx) => {
  await ctx.reply(JSON.stringify(ctx.message, null, 2));
});

bot.launch();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
