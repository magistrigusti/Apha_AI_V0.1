import test from 'node:test';
import assert from 'node:assert/strict';

import { chatWithAlpha } from './alpha-hf.js';


test('chatWithAlpha ведет диалог через /user_send и /bot_send', async () => {
  const calls = [];
  const client = {
    async predict(apiName, payload) {
      calls.push([apiName, payload]);

      if (apiName === '/user_send') {
        return {
          data: [
            '',
            [
              {
                role: 'user',
                content: 'Что такое Зион?',
              },
              {
                role: 'assistant',
                content: '...',
              },
            ],
          ],
        };
      }

      if (apiName === '/bot_send') {
        return {
          data: [
            {
              role: 'user',
              content: 'Что такое Зион?',
            },
            {
              role: 'assistant',
              content: 'Зион — столица Аллодиума.',
            },
          ],
        };
      }

      throw new Error('unexpected api call');
    },
  };

  const result = await chatWithAlpha(
    'Что такое Зион?',
    {
      client,
      chatHistory: [],
    },
  );

  assert.equal(
    result.answer,
    'Зион — столица Аллодиума.',
  );
  assert.equal(result.chatHistory.length, 2);
  assert.deepEqual(calls, [
    [
      '/user_send',
      {
        user_message: 'Что такое Зион?',
        chat_history: [],
      },
    ],
    [
      '/bot_send',
      {
        chat_history: [
          {
            role: 'user',
            content: 'Что такое Зион?',
          },
          {
            role: 'assistant',
            content: '...',
          },
        ],
      },
    ],
  ]);
});


test('chatWithAlpha откатывается на /ask, если rich chat endpoint недоступен', async () => {
  const calls = [];
  const client = {
    async predict(apiName, payload) {
      calls.push([apiName, payload]);

      if (apiName === '/user_send') {
        throw new Error('503 sleeping');
      }

      if (apiName === '/ask') {
        return {
          data: 'Аллод — это мир игры.',
        };
      }

      throw new Error('unexpected api call');
    },
  };

  const result = await chatWithAlpha(
    'Что такое Аллод?',
    {
      client,
      chatHistory: [],
    },
  );

  assert.equal(
    result.answer,
    'Аллод — это мир игры.',
  );
  assert.deepEqual(calls, [
    [
      '/user_send',
      {
        user_message: 'Что такое Аллод?',
        chat_history: [],
      },
    ],
    [
      '/ask',
      {
        msg: 'Что такое Аллод?',
      },
    ],
  ]);
  assert.deepEqual(result.chatHistory, [
    {
      role: 'user',
      content: 'Что такое Аллод?',
    },
    {
      role: 'assistant',
      content: 'Аллод — это мир игры.',
    },
  ]);
});


test('chatWithAlpha возвращает мягкий ответ при timeout HF', async () => {
  const client = {
    async predict() {
      return new Promise(() => {});
    },
  };

  const result = await chatWithAlpha(
    'Что такое Mercatus?',
    {
      client,
      timeoutMs: 5,
    },
  );

  assert.equal(
    result.answer,
    'Альфа просыпается в Hugging Face. Повтори через 20-30 секунд.',
  );
});
