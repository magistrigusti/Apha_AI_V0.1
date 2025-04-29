import { Telegraf } from 'telegraf';
import { message } from 'telegraf/filters';
import dotenv from 'dotenv';

dotenv.config();

if (!process.env.BOT_TOKEN) {
  throw new Error('BOT_TOKEN не найден в .env файле!');
}

const bot = new Telegraf(process.env.BOT_TOKEN);

bot.on(message('voice'), async ctx => {
  await ctx.reply(JSON.stringify(ctx.message.voice, null, 2));
});

bot.command('start', async (ctx) =>{
  await ctx.reply(JSON.stringify(ctx.message, null, 2));
});

bot.launch();

process.once('SICINT', () => bot.stop('SIGINT'));
process.once('SICTERM', () => bot.stop('SIGTERM'));