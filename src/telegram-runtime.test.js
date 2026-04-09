import test from 'node:test';
import assert from 'node:assert/strict';

import {
  prepareTelegramForPolling,
  startPollingAlphaBot,
} from './telegram-runtime.js';


test('prepareTelegramForPolling ничего не удаляет без webhook', async () => {
  const calls = [];
  const bot = {
    telegram: {
      async getWebhookInfo() {
        return { url: '' };
      },
      async deleteWebhook() {
        calls.push('delete');
      },
    },
  };

  const result = await prepareTelegramForPolling(
    bot,
  );

  assert.deepEqual(result, {
    removedWebhook: false,
    webhookUrl: '',
  });
  assert.deepEqual(calls, []);
});


test('prepareTelegramForPolling снимает старый webhook', async () => {
  const calls = [];
  const bot = {
    telegram: {
      async getWebhookInfo() {
        return {
          url: 'https://example.com/api/telegram',
        };
      },
      async deleteWebhook(options) {
        calls.push(options);
      },
    },
  };

  const result = await prepareTelegramForPolling(
    bot,
  );

  assert.deepEqual(result, {
    removedWebhook: true,
    webhookUrl: 'https://example.com/api/telegram',
  });
  assert.deepEqual(calls, [
    { drop_pending_updates: false },
  ]);
});


test('startPollingAlphaBot запускает bot.launch после подготовки', async () => {
  const calls = [];
  const bot = {
    telegram: {
      async getWebhookInfo() {
        calls.push('getWebhookInfo');
        return { url: '' };
      },
      async deleteWebhook() {
        calls.push('deleteWebhook');
      },
    },
    async launch() {
      calls.push('launch');
    },
  };

  const result = await startPollingAlphaBot({
    bot,
  });

  assert.equal(result.bot, bot);
  assert.deepEqual(calls, [
    'getWebhookInfo',
    'launch',
  ]);
});
