import { Telegraf } from 'telegraf';
import { message } from 'telegraf/filters';

import { askAlpha } from './alpha.js';
import { replaceWaitingMessage } from './telegram-reply.js';


export const DEFAULT_BOT_USERNAME =
  'AlphaAllod_bot';

let alphaBotInstance = null;


function buildStartMessage(botUsername) {
  return 'Приветствую, Лорд!\n'
    + 'Я Альфа — советник мира Аллодиум.\n\n'
    + 'В группе:\n'
    + '/ask <вопрос>\n'
    + 'или @' + botUsername
    + ' <вопрос>\n\n'
    + 'В личке — просто пиши.';
}


function extractAskQuestion(text, botUsername) {
  return text
    .replace('/ask', '')
    .replace('@' + botUsername, '')
    .trim();
}


export function registerAlphaBotHandlers(
  bot,
  options = {},
) {
  const botUsername =
    options.botUsername
    ?? process.env.ALPHA_BOT_USERNAME
    ?? DEFAULT_BOT_USERNAME;
  const ask =
    options.askAlpha
    ?? askAlpha;

  // ========== /start ==========
  bot.command('start', async (ctx) => {
    await ctx.reply(
      buildStartMessage(botUsername),
    );
  });

  // ========== /ask ==========
  bot.command('ask', async (ctx) => {
    const question = extractAskQuestion(
      ctx.message.text,
      botUsername,
    );

    if (!question) {
      await ctx.reply(
        'Напиши вопрос после /ask\n'
        + 'Пример: /ask Что такое Аллод?',
      );
      return;
    }

    const wait = await ctx.reply('Думаю…');
    const answer = await ask(question);

    await replaceWaitingMessage(
      ctx,
      wait.message_id,
      answer,
    );
  });

  // ========== ТЕКСТОВЫЕ СООБЩЕНИЯ ==========
  bot.on(message('text'), async (ctx) => {
    const text = ctx.message.text;
    const isPrivate =
      ctx.chat.type === 'private';

    if (isPrivate) {
      const wait = await ctx.reply('Думаю…');
      const answer = await ask(text);

      await replaceWaitingMessage(
        ctx,
        wait.message_id,
        answer,
      );
      return;
    }

    const mentioned = text.includes(
      '@' + botUsername,
    );
    const botId = ctx.botInfo?.id;
    const isReply =
      Boolean(botId)
      && ctx.message.reply_to_message
        ?.from?.id === botId;

    if (!mentioned && !isReply) return;

    const question = text
      .replace('@' + botUsername, '')
      .trim();

    if (!question) return;

    const wait = await ctx.reply('Думаю…');
    const answer = await ask(question);

    await replaceWaitingMessage(
      ctx,
      wait.message_id,
      answer,
    );
  });

  return bot;
}


export function createAlphaBot(
  options = {},
) {
  const token =
    options.token
    ?? process.env.ALPHA_BOT_TOKEN;

  if (!token) {
    throw new Error(
      'ALPHA_BOT_TOKEN is not set',
    );
  }

  const bot = new Telegraf(token);
  return registerAlphaBotHandlers(
    bot,
    options,
  );
}


export function getAlphaBot(
  options = {},
) {
  if (!alphaBotInstance) {
    alphaBotInstance = createAlphaBot(
      options,
    );
  }

  return alphaBotInstance;
}
