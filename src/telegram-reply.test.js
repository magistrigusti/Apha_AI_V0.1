import test from 'node:test';
import assert from 'node:assert/strict';

import { replaceWaitingMessage } from './telegram-reply.js';

test('replaceWaitingMessage редактирует сообщение если edit работает', async () => {
  const calls = [];
  const ctx = {
    chat: {
      id: 101,
    },
    telegram: {
      async editMessageText(chatId, messageId, inlineMessageId, text) {
        calls.push([chatId, messageId, inlineMessageId, text]);
      },
    },
    async reply() {
      throw new Error('reply не должен вызываться');
    },
  };

  await replaceWaitingMessage(ctx, 55, 'Ответ Альфы');

  assert.deepEqual(calls, [
    [101, 55, null, 'Ответ Альфы'],
  ]);
});

test('replaceWaitingMessage отправляет новый ответ если editMessageText не нашел сообщение', async () => {
  const calls = [];
  const ctx = {
    chat: {
      id: 101,
    },
    telegram: {
      async editMessageText() {
        const error = new Error('message to edit not found');
        error.response = {
          description: 'Bad Request: message to edit not found',
        };
        throw error;
      },
    },
    async reply(text) {
      calls.push(text);
    },
  };

  await replaceWaitingMessage(ctx, 55, 'Ответ Альфы');

  assert.deepEqual(calls, ['Ответ Альфы']);
});

test('replaceWaitingMessage пробрасывает чужие ошибки telegram дальше', async () => {
  const ctx = {
    chat: {
      id: 101,
    },
    telegram: {
      async editMessageText() {
        const error = new Error('forbidden');
        error.response = {
          description: 'Bad Request: forbidden',
        };
        throw error;
      },
    },
    async reply() {},
  };

  await assert.rejects(
    () => replaceWaitingMessage(ctx, 55, 'Ответ Альфы'),
    /forbidden/,
  );
});
