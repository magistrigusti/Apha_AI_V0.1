# OpenClaw — установка и запуск

OpenClaw — персональный AI-ассистент с мультиканальными каналами
(Telegram, WhatsApp, Slack, Discord и др.).

## Требования

- **Node.js ≥ 22** (проверь: `node -v`)
- npm 10+ или pnpm 9+
- **LLM провайдер** — OpenAI или Anthropic (API ключ)

## Установка

```bash
npm install
```

После установки OpenClaw будет в `node_modules`.

## Первый запуск (Onboarding)

1. Запусти мастер настройки:

```bash
npm run openclaw:onboard
```

Мастер спросит:
- Модель (OpenAI/Anthropic)
- API ключи
- Каналы (Telegram, WhatsApp и т.д.)
- Установить ли daemon (фоновый сервис)

2. Для Telegram укажи токен бота.
   - Можно использовать отдельный бот или `ALPHA_BOT_TOKEN`
   - OpenClaw использует `TELEGRAM_BOT_TOKEN` или `channels.telegram.botToken`

## Запуск Gateway

```bash
npm run openclaw:gateway
```

Gateway будет на `http://127.0.0.1:18789/` — Dashboard и WebChat.

## Проверка

```bash
npm run openclaw:doctor
```

## Отличие от нашей Альфы

| | Альфа (наш бот) | OpenClaw |
|--|-----------------|----------|
| Мозг | HF Space (Qwen) | OpenAI/Anthropic |
| Каналы | Telegram | Telegram, WhatsApp, Slack, Discord и др. |
| Конфиг | `.env` | `~/.openclaw/openclaw.json` |
| Запуск | `npm run dev` | `npm run openclaw:gateway` |

OpenClaw — полноценный ассистент со своими моделями.
Наша Альфа — советник Аллода на HF Space.

Можно запускать оба:
- Альфа — для вопросов по Allodium
- OpenClaw — для общего AI-ассистента

## Deploy на Render

1. В Render: **New → Blueprint**
2. Подключи репо `Apha_AI_V0.1`
3. Выбери файл `render-openclaw.yaml`
4. Добавь переменные: `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY` (или Anthropic)
5. Deploy

Образ: `ghcr.io/openclaw/openclaw:latest`
