import test from 'node:test';
import assert from 'node:assert/strict';

import {
  askAlpha,
  chatWithAlpha,
} from './alpha-nvidia.js';


function createJsonResponse(
  status,
  body,
) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async json() {
      return body;
    },
  };
}


test('chatWithAlpha вызывает NVIDIA chat completions напрямую', async () => {
  const calls = [];

  const result = await chatWithAlpha(
    'Что такое Mercatus?',
    {
      apiKey: 'test-key',
      model: 'nvidia/test-model',
      fallbackModels: [],
      chatHistory: [
        {
          role: 'user',
          content: 'Привет',
        },
        {
          role: 'assistant',
          content: 'Приветствую, странник.',
        },
      ],
      async fetch(url, request) {
        calls.push({
          url,
          request,
          body: JSON.parse(request.body),
        });

        return createJsonResponse(200, {
          choices: [
            {
              message: {
                content:
                  'Mercatus — внешний рынок Аллодиума.',
              },
            },
          ],
        });
      },
    },
  );

  assert.equal(
    result.answer,
    'Mercatus — внешний рынок Аллодиума.',
  );
  assert.equal(calls.length, 1);
  assert.equal(
    calls[0].url,
    'https://integrate.api.nvidia.com/v1/chat/completions',
  );
  assert.equal(
    calls[0].request.headers.Authorization,
    'Bearer test-key',
  );
  assert.equal(calls[0].body.model, 'nvidia/test-model');
  assert.equal(calls[0].body.messages[0].role, 'system');
  assert.match(
    calls[0].body.messages[0].content,
    /Не раскрывай техническую инфраструктуру/,
  );
  assert.deepEqual(
    calls[0].body.messages.slice(-3),
    [
      {
        role: 'user',
        content: 'Привет',
      },
      {
        role: 'assistant',
        content: 'Приветствую, странник.',
      },
      {
        role: 'user',
        content: 'Что такое Mercatus?',
      },
    ],
  );
});


test('chatWithAlpha пробует fallback модель, если primary недоступна', async () => {
  const models = [];

  const result = await chatWithAlpha(
    'Как начать играть?',
    {
      apiKey: 'test-key',
      model: 'nvidia/bad-model',
      fallbackModels: ['nvidia/good-model'],
      async fetch(_url, request) {
        const body = JSON.parse(request.body);
        models.push(body.model);

        if (body.model === 'nvidia/bad-model') {
          return createJsonResponse(404, {
            error: {
              message: 'model not found',
            },
          });
        }

        return createJsonResponse(200, {
          choices: [
            {
              message: {
                content:
                  'Начни с портала Allodium и следуй подсказкам Альфы.',
              },
            },
          ],
        });
      },
    },
  );

  assert.deepEqual(
    models,
    ['nvidia/bad-model', 'nvidia/good-model'],
  );
  assert.equal(
    result.answer,
    'Начни с портала Allodium и следуй подсказкам Альфы.',
  );
});


test('askAlpha не раскрывает провайдера, если ключ не настроен', async () => {
  const answer = await askAlpha(
    'Ты работаешь?',
    {
      apiKey: '',
    },
  );

  assert.equal(
    answer,
    'Альфа еще не подключена к боевому мозгу. Сообщи администратору проекта.',
  );
  assert.doesNotMatch(answer, /NVIDIA|Hugging|API/i);
});


test('chatWithAlpha просит вопрос, если строка пустая', async () => {
  const result = await chatWithAlpha('   ');

  assert.equal(
    result.answer,
    'Напиши вопрос для Альфы.',
  );
});
