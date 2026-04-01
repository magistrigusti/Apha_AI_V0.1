# Альфа — глобальный деплой на Render

Бот работает в облаке 24/7, отвечает в Telegram.
**Groq API** — без Hugging Face, без "Starting", быстрый ответ.

---

## Быстрый старт (Blueprint)

1. Зайди на [dashboard.render.com](https://dashboard.render.com)
2. **New → Blueprint**
3. Подключи репо `magistrigusti/Apha_AI_V0.1`
4. Render подхватит `render.yaml` — нажми **Apply**
5. В настройках сервиса **alpha-bot** добавь переменные:
   - `ALPHA_BOT_TOKEN` = токен от @BotFather
   - `GROQ_API_KEY` = ключ с [console.groq.com](https://console.groq.com) (бесплатно)
6. Дождись деплоя (2–3 мин)

Готово. Бот работает глобально.

---

## Ручной деплой

**New → Web Service** (не Background Worker):

| Поле | Значение |
|------|----------|
| Build | `npm install` |
| Start | `npm start` |
| Env | `ALPHA_BOT_TOKEN`, `GROQ_API_KEY` |

---

## Не дать сервису засыпать (free tier)

Render останавливает сервис через ~15 мин без запросов.

[cron-job.org](https://cron-job.org) → задача каждые 14 мин на URL сервиса.

---

## Проверка

- URL в браузере: «Альфа в сети! Зион на связи.»
- Telegram @AlphaAllod_bot — пиши вопрос
