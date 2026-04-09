# Альфа — Telegram бот на Render

Бот работает в облаке 24/7 и отвечает в Telegram.
Источник ответа — Hugging Face Space Альфы.

---

## Как это работает

`Telegram -> Render bot -> HF Space /ask -> ответ игроку`

Важно:
- Render-версия использует `polling`
- если раньше у бота был webhook, новый старт сам снимает его
- поэтому после деплоя Render-бот не должен упираться в `409 conflict`

---

## Быстрый старт (Blueprint)

1. Зайди на [dashboard.render.com](https://dashboard.render.com)
2. Выбери **New -> Blueprint**
3. Подключи репо `magistrigusti/Apha_Friend-gamers-allodium`
4. Render подхватит `render.yaml` — нажми **Apply**
5. В настройках сервиса **alpha-bot** заполни переменные:
   - `ALPHA_BOT_TOKEN` = токен от @BotFather
   - `ALPHA_SPACE_ID` = `magistrigusti/allod-alpha`
   - `HF_TOKEN` = нужен только если Space приватный
6. Дождись деплоя

---

## Ручной деплой

Создай **Web Service**:

| Поле | Значение |
|------|----------|
| Build | `npm install` |
| Start | `npm start` |
| Env | `ALPHA_BOT_TOKEN`, `ALPHA_SPACE_ID`, `HF_TOKEN` |

`ALPHA_SPACE_ID` по умолчанию:

```text
magistrigusti/allod-alpha
```

---

## Что важно проверить

1. В логах Render должен быть:
   - `[Server] Port ...`
   - `[Alpha Bot] Started!`
2. Если раньше бот работал через webhook, в логах может появиться:
   - `[Alpha Bot] Removed webhook for polling mode: ...`
3. В браузере URL сервиса должен отвечать:
   - `Альфа в сети! Зион на связи.`

---

## Если Telegram всё ещё молчит

Проверь:
- верный ли `ALPHA_BOT_TOKEN`
- не запущен ли где-то второй экземпляр этого же бота
- доступны ли логи Render
- отвечает ли сам HF Space в браузере

---

## Проверка

- URL сервиса в браузере: `Альфа в сети! Зион на связи.`
- Telegram `@AlphaAllod_bot` — отправь `/start`
- потом отправь `/ask Что такое Аллод?`
