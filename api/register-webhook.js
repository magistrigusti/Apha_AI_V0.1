import {
  registerTelegramWebhook,
} from '../src/vercel-telegram.js';


export default async function handler(
  req,
  res,
) {
  try {
    await registerTelegramWebhook(
      req,
      res,
    );
  } catch (error) {
    console.error(
      '[Register Webhook]',
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
