import { createAlphaBot } from './alpha-bot.js';


function normalizeWebhookUrl(info) {
  if (!info || typeof info.url !== 'string') {
    return '';
  }

  return info.url.trim();
}


// ========== ПОДГОТОВКА POLLING РЕЖИМА ==========
export async function prepareTelegramForPolling(bot) {
  const info = await bot.telegram.getWebhookInfo();
  const webhookUrl = normalizeWebhookUrl(info);

  if (!webhookUrl) {
    return {
      removedWebhook: false,
      webhookUrl: '',
    };
  }

  await bot.telegram.deleteWebhook({
    drop_pending_updates: false,
  });

  return {
    removedWebhook: true,
    webhookUrl,
  };
}


// ========== ЗАПУСК БОТА ЧЕРЕЗ POLLING ==========
export async function startPollingAlphaBot(
  options = {},
) {
  const bot =
    options.bot ?? createAlphaBot(options);

  const state = await prepareTelegramForPolling(
    bot,
  );

  await bot.launch();

  return {
    bot,
    ...state,
  };
}
