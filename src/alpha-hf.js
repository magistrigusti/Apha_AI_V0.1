import { Client } from '@gradio/client';

const DEFAULT_ALPHA_SPACE_ID =
  'magistrigusti/allod-alpha';
const DEFAULT_EMPTY_QUESTION_MESSAGE =
  'Напиши вопрос для Альфы.';
const DEFAULT_NO_ANSWER_MESSAGE =
  'Нет ответа.';
const DEFAULT_ALPHA_REQUEST_TIMEOUT_MS = 5000;

let alphaClientPromise = null;
let alphaClientKey = '';


function getAlphaRequestTimeoutMs(options = {}) {
  const rawValue =
    options.timeoutMs
    ?? process.env.ALPHA_REQUEST_TIMEOUT_MS
    ?? DEFAULT_ALPHA_REQUEST_TIMEOUT_MS;
  const parsedValue = Number.parseInt(
    String(rawValue),
    10,
  );

  if (
    Number.isFinite(parsedValue)
    && parsedValue > 0
  ) {
    return parsedValue;
  }

  return DEFAULT_ALPHA_REQUEST_TIMEOUT_MS;
}


async function withAlphaTimeout(
  promise,
  label,
  options = {},
) {
  const timeoutMs =
    getAlphaRequestTimeoutMs(options);
  let timeoutId;

  const timeoutPromise = new Promise(
    (_, reject) => {
      timeoutId = setTimeout(() => {
        reject(
          new Error(
            `${label} timeout after ${timeoutMs}ms`,
          ),
        );
      }, timeoutMs);
    },
  );

  try {
    return await Promise.race([
      promise,
      timeoutPromise,
    ]);
  } finally {
    clearTimeout(timeoutId);
  }
}


async function predictWithTimeout(
  client,
  apiName,
  payload,
  options = {},
) {
  const timeoutMs =
    getAlphaRequestTimeoutMs(options);
  let timeoutId;
  const label = `Alpha ${apiName}`;

  const timeoutPromise = new Promise(
    (_, reject) => {
      timeoutId = setTimeout(() => {
        client.close?.();
        reject(
          new Error(
            `${label} timeout after ${timeoutMs}ms`,
          ),
        );
      }, timeoutMs);
    },
  );

  try {
    return await Promise.race([
      client.predict(apiName, payload),
      timeoutPromise,
    ]);
  } finally {
    clearTimeout(timeoutId);
  }
}


function getAlphaErrorMessage(error) {
  if (error instanceof Error && error.message) {
    return error.message;
  }

  if (typeof error === 'string') {
    return error;
  }

  if (error && typeof error === 'object') {
    for (const key of ['message', 'error', 'detail']) {
      const value = error[key];
      if (typeof value === 'string' && value.trim()) {
        return value.trim();
      }
    }

    try {
      return JSON.stringify(error);
    } catch {
      return String(error);
    }
  }

  return String(error ?? '');
}


function extractText(value) {
  if (typeof value === 'string') {
    return value.trim();
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => extractText(item))
      .filter(Boolean)
      .join('\n')
      .trim();
  }

  if (value && typeof value === 'object') {
    if ('content' in value) {
      const contentText = extractText(
        value.content,
      );
      if (contentText) {
        return contentText;
      }
    }

    for (const key of [
      'text',
      'value',
      'path',
      'url',
      'orig_name',
    ]) {
      const nextValue = value[key];
      if (
        typeof nextValue === 'string'
        && nextValue.trim()
      ) {
        return nextValue.trim();
      }
    }
  }

  return '';
}


function normalizeChatHistory(chatHistory) {
  if (!Array.isArray(chatHistory)) {
    return [];
  }

  return chatHistory.flatMap((entry) => {
    if (!entry || typeof entry !== 'object') {
      return [];
    }

    const role = entry.role;
    if (
      role !== 'user'
      && role !== 'assistant'
      && role !== 'system'
    ) {
      return [];
    }

    if (!('content' in entry)) {
      return [];
    }

    return [{ ...entry, role }];
  });
}


function buildFallbackChatHistory(
  chatHistory,
  question,
  answer,
) {
  return [
    ...normalizeChatHistory(chatHistory),
    {
      role: 'user',
      content: question,
    },
    {
      role: 'assistant',
      content: answer,
    },
  ];
}


function extractChatHistory(result) {
  const data = result?.data;

  if (!Array.isArray(data)) {
    return [];
  }

  if (data.length > 1 && Array.isArray(data[1])) {
    return normalizeChatHistory(data[1]);
  }

  if (
    data.every(
      (item) =>
        item
        && typeof item === 'object'
        && !Array.isArray(item)
        && 'role' in item,
    )
  ) {
    return normalizeChatHistory(data);
  }

  return [];
}


function extractLatestAssistantAnswer(
  chatHistory,
) {
  for (
    let index = chatHistory.length - 1;
    index >= 0;
    index -= 1
  ) {
    const entry = chatHistory[index];
    if (entry?.role !== 'assistant') {
      continue;
    }

    const text = extractText(entry.content);
    if (
      text
      && text !== '...'
      && text !== '…'
    ) {
      return text;
    }
  }

  return '';
}


async function getAlphaClient(options = {}) {
  const spaceId =
    options.spaceId
    ?? process.env.ALPHA_SPACE_ID
    ?? DEFAULT_ALPHA_SPACE_ID;
  const token =
    options.token
    ?? process.env.HF_TOKEN
    ?? null;
  const nextKey = `${spaceId}:${token ?? ''}`;

  if (!alphaClientPromise || alphaClientKey !== nextKey) {
    alphaClientKey = nextKey;
    alphaClientPromise = withAlphaTimeout(
      Client.connect(
        spaceId,
        token ? { token } : undefined,
      ),
      'Alpha connect',
      options,
    ).catch((error) => {
      alphaClientPromise = null;
      throw error;
    });
  }

  return alphaClientPromise;
}


function getAlphaFailureReply(messageText) {
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
    || messageText.includes('timeout')
    || messageText.includes('503')
    || messageText.includes('terminated')
    || messageText.includes('UND_ERR_SOCKET')
    || messageText.includes('Connection errored out')
  ) {
    return 'Альфа просыпается в Hugging Face. Повтори через 20-30 секунд.';
  }

  return 'Альфа временно недоступна в Hugging Face.';
}


export function extractAlphaAnswer(result) {
  if (typeof result === 'string') {
    return result.trim() || DEFAULT_NO_ANSWER_MESSAGE;
  }

  if (typeof result?.data === 'string') {
    return result.data.trim() || DEFAULT_NO_ANSWER_MESSAGE;
  }

  const chatHistory = extractChatHistory(result);
  const latestAnswer =
    extractLatestAssistantAnswer(chatHistory);

  if (latestAnswer) {
    return latestAnswer;
  }

  const text = extractText(result?.data);
  return text || DEFAULT_NO_ANSWER_MESSAGE;
}


export async function chatWithAlpha(
  message,
  options = {},
) {
  const question = String(message ?? '').trim();
  const initialHistory = normalizeChatHistory(
    options.chatHistory,
  );

  if (!question) {
    return {
      answer: DEFAULT_EMPTY_QUESTION_MESSAGE,
      chatHistory: initialHistory,
    };
  }

  try {
    const client =
      options.client ?? await getAlphaClient(options);

    if (options.chatHistory !== undefined) {
      try {
        const userSendResult = await predictWithTimeout(
          client,
          '/user_send',
          {
            user_message: question,
            chat_history: initialHistory,
          },
          options,
        );

        const historyAfterUser =
          extractChatHistory(userSendResult);
        const nextUserHistory =
          historyAfterUser.length > 0
            ? historyAfterUser
            : [
                ...initialHistory,
                {
                  role: 'user',
                  content: question,
                },
              ];

        const botSendResult = await predictWithTimeout(
          client,
          '/bot_send',
          {
            chat_history: nextUserHistory,
          },
          options,
        );

        const nextHistory =
          extractChatHistory(botSendResult);
        const answer =
          extractAlphaAnswer(botSendResult);

        return {
          answer,
          chatHistory:
            nextHistory.length > 0
              ? nextHistory
              : buildFallbackChatHistory(
                  initialHistory,
                  question,
                  answer,
                ),
        };
      } catch (error) {
        const messageText =
          getAlphaErrorMessage(error);
        console.warn(
          '[Alpha HF] Conversation endpoints failed:',
          messageText,
        );

        if (messageText.includes('timeout')) {
          throw error;
        }

        console.warn('[Alpha HF] Falling back to /ask');
      }
    }

    const result = await predictWithTimeout(
      client,
      '/ask',
      { msg: question },
      options,
    );
    const answer = extractAlphaAnswer(result);

    return {
      answer,
      chatHistory: buildFallbackChatHistory(
        initialHistory,
        question,
        answer,
      ),
    };
  } catch (error) {
    const messageText = getAlphaErrorMessage(error);

    console.error('[Alpha HF]', messageText);

    return {
      answer: getAlphaFailureReply(messageText),
      chatHistory: initialHistory,
    };
  }
}


export async function askAlpha(
  message,
  options = {},
) {
  const result = await chatWithAlpha(
    message,
    options,
  );
  return result.answer;
}
