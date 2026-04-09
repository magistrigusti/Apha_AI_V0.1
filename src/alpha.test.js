import test from 'node:test';
import assert from 'node:assert/strict';

import { askAlpha, extractAlphaAnswer } from './alpha.js';


test('askAlpha отправляет msg в endpoint /ask', async () => {
  const calls = [];
  const client = {
    async predict(apiName, payload) {
      calls.push({ apiName, payload });
      return { data: 'Ответ Альфы' };
    },
  };

  const answer = await askAlpha(
    'Что такое Аллод?',
    { client },
  );

  assert.equal(answer, 'Ответ Альфы');
  assert.deepEqual(calls, [
    {
      apiName: '/ask',
      payload: { msg: 'Что такое Аллод?' },
    },
  ]);
});


test('askAlpha просит ввести вопрос если строка пустая', async () => {
  const client = {
    async predict() {
      throw new Error('predict should not be called');
    },
  };

  const answer = await askAlpha('   ', { client });
  assert.equal(answer, 'Напиши вопрос для Альфы.');
});


test('extractAlphaAnswer достает текст из ответа Gradio', () => {
  const result = {
    data: ['Альфа на связи.'],
  };

  assert.equal(
    extractAlphaAnswer(result),
    'Альфа на связи.',
  );
});

test('askAlpha вызывает endpoint /ask у HF Space', async () => {
  const calls = [];
  const fakeClient = {
    async predict(apiName, payload) {
      calls.push([apiName, payload]);
      return {
        data: ['Ответ из Space'],
      };
    },
  };

  const answer = await askAlpha(
    'Что такое Зион?',
    {
      client: fakeClient,
    },
  );

  assert.equal(answer, 'Ответ из Space');
  assert.deepEqual(calls, [
    ['/ask', { msg: 'Что такое Зион?' }],
  ]);
});
