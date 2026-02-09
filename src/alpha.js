// src/alpha.js
// ========================================
// Клиент для HF Space — мозг Альфы
// ========================================

import { Client } from '@gradio/client';

const SPACE_ID =
  'magistrigusti/allod-alpha';

let client = null;

// ========== ПОДКЛЮЧЕНИЕ К SPACE ==========
// Ленивое — подключаемся при первом запросе
async function getClient() {
  if (!client) {
    console.log(
      '[Alpha] Connecting to Space...'
    );
    client = await Client.connect(SPACE_ID);
    console.log('[Alpha] Connected!');
  }
  return client;
}


// ========== ЗАПРОС К АЛЬФЕ ==========
export async function askAlpha(message) {
  try {
    const c = await getClient();

    // Вызываем API endpoint "/ask"
    const result = await c.predict(
      '/ask',
      [message],
    );

    return result.data[0];
  } catch (error) {
    console.error(
      '[Alpha] Error:',
      error.message,
    );

    // Сброс клиента при ошибке
    client = null;

    // Space спит — будим
    if (
      error.message?.includes('timeout')
      || error.message?.includes('Could not')
    ) {
      return (
        'Альфа просыпается… '
        + 'Попробуй через 30 секунд.'
      );
    }

    return 'Альфа временно недоступна.';
  }
}