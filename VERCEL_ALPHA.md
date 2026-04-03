# Альфа — deploy на Vercel

Альфа работает так:

`Telegram -> Vercel webhook -> HF Space -> ответ игроку`

## Env для Vercel

- `ALPHA_BOT_TOKEN`
- `ALPHA_SPACE_ID`
- `HF_TOKEN` — только если Space приватный
- `TELEGRAM_WEBHOOK_SECRET`
- `TELEGRAM_WEBHOOK_SETUP_TOKEN`

## Endpoint'ы

- `POST /api/telegram` — webhook от Telegram
- `GET/POST /api/register-webhook` — одноразовая регистрация webhook

## Запуск

1. Задеплой проект на Vercel
2. Добавь env-переменные в проект
3. Открой production URL:

```text
https://<your-domain>/api/register-webhook
```

4. Передай header:

```text
x-webhook-setup-token: <TELEGRAM_WEBHOOK_SETUP_TOKEN>
```

5. Telegram начнет слать update в:

```text
https://<your-domain>/api/telegram
```

## Важно

- В production не нужен `bot.launch()`
- Локальный `src/main.js` остается только для dev
- Если HF Space спит, первый ответ может быть медленнее
