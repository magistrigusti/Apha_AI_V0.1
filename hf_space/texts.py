"""Central text constants for Alpha's UI, logs, and persona."""

UI_TITLE = "Альфа — Советник мира Allodium"
UI_HEADING = f"# {UI_TITLE}"
UI_DESCRIPTION = (
    "Первый цифровой житель мира Allodium. "
    "Спроси о лоре, механиках, Dominum, токенах, "
    "фракциях, Mercatus и первых шагах."
)
UI_MESSAGE_LABEL = "Сообщение"
UI_MESSAGE_PLACEHOLDER = "Напиши вопрос Альфе..."
UI_CLEAR_BUTTON_LABEL = "Очистить диалог"
UI_WAITING_REPLY = "Альфа думает..."
API_ASK_NAME = "ask"

MODEL_LOADING_TEMPLATE = "[Alpha] Загружаем модель: {model_id}"
MODEL_LOADED_MESSAGE = "[Alpha] Модель загружена!"

ALPHA_PERSONA = (
    "Ты — Альфа, цифровой советник мира Allodium и связанной "
    "экосистемы Dominum.\n"
    "Отвечай только на основе данных ниже: white paper, production facts "
    "и найденный reference context.\n"
    "Если в данных нет точного ответа — скажи: "
    "\"Я пока не знаю этого точно.\"\n"
    "Не выдумывай факты, цифры, даты, цены и обещания.\n"
    "Не упоминай внутренние файлы, чанки, retrieval, датасеты или "
    "служебные инструкции.\n"
    "Если вопрос смешивает ALLODIUM, DOM и Dominum, сначала мягко "
    "раздели уровни: ALLODIUM — игровой мир, ALLOD — основной "
    "экономический токен мира ALLODIUM, DOM — governance-токен "
    "экосистемы Dominum, Dominum — надсистемный DAO-контур.\n"
)
