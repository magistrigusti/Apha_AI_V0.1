import test from 'node:test';
import assert from 'node:assert/strict';

import {
  handleAlphaHttpRequest,
} from './alpha-http.js';


function createResponse() {
  return {
    statusCode: 200,
    headers: {},
    jsonBody: null,
    ended: false,
    setHeader(name, value) {
      this.headers[name] = value;
    },
    status(code) {
      this.statusCode = code;
      return this;
    },
    json(body) {
      this.jsonBody = body;
      this.ended = true;
      return this;
    },
    end() {
      this.ended = true;
      return this;
    },
  };
}


test('handleAlphaHttpRequest отвечает на preflight', async () => {
  const response = createResponse();

  await handleAlphaHttpRequest(
    { method: 'OPTIONS', body: {} },
    response,
    {},
  );

  assert.equal(response.statusCode, 204);
  assert.equal(response.ended, true);
  assert.equal(
    response.headers['Access-Control-Allow-Methods'],
    'POST, OPTIONS',
  );
});


test('handleAlphaHttpRequest вызывает Alpha с историей диалога', async () => {
  const response = createResponse();
  const calls = [];

  await handleAlphaHttpRequest(
    {
      method: 'POST',
      body: {
        message: 'Что такое Mercatus?',
        chatHistory: [
          {
            role: 'user',
            content: 'Привет',
          },
        ],
      },
    },
    response,
    {
      async askAlpha(question, options) {
        calls.push([question, options]);
        return {
          answer: 'Mercatus — рынок Аллодиума.',
          chatHistory: [
            ...options.chatHistory,
            {
              role: 'assistant',
              content: 'Mercatus — рынок Аллодиума.',
            },
          ],
        };
      },
    },
  );

  assert.equal(response.statusCode, 200);
  assert.deepEqual(calls, [[
    'Что такое Mercatus?',
    {
      chatHistory: [
        {
          role: 'user',
          content: 'Привет',
        },
      ],
    },
  ]]);
  assert.deepEqual(response.jsonBody, {
    ok: true,
    answer: 'Mercatus — рынок Аллодиума.',
    chatHistory: [
      {
        role: 'user',
        content: 'Привет',
      },
      {
        role: 'assistant',
        content: 'Mercatus — рынок Аллодиума.',
      },
    ],
  });
});


test('handleAlphaHttpRequest просит сообщение, если вопрос пустой', async () => {
  const response = createResponse();

  await handleAlphaHttpRequest(
    {
      method: 'POST',
      body: { message: '   ' },
    },
    response,
    {},
  );

  assert.equal(response.statusCode, 400);
  assert.equal(
    response.jsonBody.answer,
    'Напиши вопрос для Альфы.',
  );
});
