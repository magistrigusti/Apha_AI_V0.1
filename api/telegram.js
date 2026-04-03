import {
  handleTelegramWebhook,
} from '../src/vercel-telegram.js';


export default async function handler(
  req,
  res,
) {
  try {
    await handleTelegramWebhook(
      req,
      res,
    );
  } catch (error) {
    console.error(
      '[Vercel Telegram]',
      error,
    );

    if (!res.writableEnded && !res.ended) {
      res.status(500).json({
        ok: false,
        error: 'Internal Server Error',
      });
    }
  }
}
