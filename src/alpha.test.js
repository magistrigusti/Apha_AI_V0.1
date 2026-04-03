import test from 'node:test';
import assert from 'node:assert/strict';

import { askAlpha, extractAlphaAnswer } from './alpha.js';

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
    ['/ask', ['Что такое Зион?']],
  ]);
});
