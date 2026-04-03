// src/alpha.js
// ========================================
// Альфа — через Hugging Face Space
// Один источник истины для Telegram
// ========================================

import { Client } from '@gradio/client';

const DEFAULT_ALPHA_SPACE_ID =
  'magistrigusti/allod-alpha';

let alphaClientPromise = null;
let alphaClientKey = '';


export function extractAlphaAnswer(result) {
  if (typeof result === 'string') {
    return result.trim() || 'Нет ответа.';
  }

  if (typeof result?.data === 'string') {
    return result.data.trim() || 'Нет ответа.';
  }

  if (Array.isArray(result?.data)) {
    const [firstItem] = result.data;
    if (typeof firstItem === 'string') {
      return firstItem.trim() || 'Нет ответа.';
    }
  }

  return 'Нет ответа.';
}


// ========== ЗАПРОС К HF SPACE ==========
export async function askAlpha(message, options = {}) {
  const question = String(message ?? '').trim();
  if (!question) {
    return 'Напиши вопрос для Альфы.';
  }

  const spaceId =
    options.spaceId
    ?? process.env.ALPHA_SPACE_ID
    ?? DEFAULT_ALPHA_SPACE_ID;
  const token =
    options.token
    ?? process.env.HF_TOKEN
    ?? null;

  try {
    const client = options.client ?? await (async () => {
      const nextKey = `${spaceId}:${token ?? ''}`;
      if (!alphaClientPromise || alphaClientKey !== nextKey) {
        alphaClientKey = nextKey;
        alphaClientPromise = Client.connect(
          spaceId,
          token ? { token } : undefined,
        ).catch((error) => {
          alphaClientPromise = null;
          throw error;
        });
      }

      return alphaClientPromise;
    })();

    const result = await client.predict(
      '/ask',
      [question],
    );

    return extractAlphaAnswer(result);
  } catch (error) {
    const messageText =
      error instanceof Error
        ? error.message
        : String(error);

    console.error('[Alpha HF]', messageText);

    if (messageText.includes('404')) {
      return 'Не найден Hugging Face Space Альфы.';
    }

    if (
      messageText.includes('429')
      || messageText.includes('rate limit')
    ) {
      return 'Лимит Hugging Face. Попробуй чуть позже.';
    }

    if (
      messageText.includes('loading')
      || messageText.includes('sleep')
      || messageText.includes('503')
    ) {
      return 'Альфа просыпается в Hugging Face. Повтори через 20-30 секунд.';
    }

    return 'Альфа временно недоступна в Hugging Face.';
  }
}
