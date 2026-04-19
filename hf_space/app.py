# ========================================
# app.py — Gradio UI для Альфы
# Точка входа HF Space
# ========================================

import gradio as gr
from model import reply
from texts import (
    API_ASK_NAME,
    UI_CLEAR_BUTTON_LABEL,
    UI_DESCRIPTION,
    UI_HEADING,
    UI_MESSAGE_LABEL,
    UI_MESSAGE_PLACEHOLDER,
    UI_TITLE,
    UI_WAITING_REPLY,
)


# ========== ИНТЕРФЕЙС ==========
with gr.Blocks(
    title=UI_TITLE,
) as demo:

    # ========== ЗАГОЛОВОК ==========
    gr.Markdown(UI_HEADING)
    gr.Markdown(UI_DESCRIPTION)
    # ========== ЧАТ ==========
    chat = gr.Chatbot(
        height=420,
    )

    # ========== ПОЛЕ ВВОДА ==========
    msg = gr.Textbox(
        label=UI_MESSAGE_LABEL,
        placeholder=UI_MESSAGE_PLACEHOLDER,
    )

    # ========== КНОПКА ОЧИСТКИ ==========
    clear = gr.Button(UI_CLEAR_BUTTON_LABEL)

    # ========== ОБРАБОТЧИКИ ==========
    def user_send(user_message, chat_history):
        """Отправка сообщения от игрока"""
        chat_history = list(chat_history or [])
        if not user_message or not user_message.strip():
            return "", chat_history

        chat_history.append({
            "role": "user",
            "content": user_message,
        })
        # Заглушка пока генерируется ответ
        chat_history.append({
            "role": "assistant",
            "content": UI_WAITING_REPLY,
        })
        return "", chat_history

    def bot_send(chat_history):
        """Генерация ответа Альфы"""
        chat_history = list(chat_history or [])
        if len(chat_history) < 2:
            return chat_history

        # Сообщение игрока — предпоследнее
        user_message = chat_history[-2]["content"]

        # История без текущей пары
        history_before = chat_history[:-2]

        answer = reply(
            user_message,
            history_before,
        )

        # Заменяем заглушку на ответ
        chat_history[-1]["content"] = answer
        return chat_history

    # ========== СОБЫТИЯ UI ==========
    msg.submit(
        user_send,
        inputs=[msg, chat],
        outputs=[msg, chat],
        queue=False,
    ).then(
        bot_send,
        inputs=chat,
        outputs=chat,
    )

    clear.click(
        lambda: [],
        None,
        chat,
        queue=False,
    )

    # ========== API ДЛЯ TELEGRAM БОТА ==========
    # Скрытые элементы — не видны в UI
    api_input = gr.Textbox(visible=False)
    api_output = gr.Textbox(visible=False)
    api_btn = gr.Button(visible=False)

    api_btn.click(
        fn=lambda msg: reply(msg, []),
        inputs=api_input,
        outputs=api_output,
        api_name=API_ASK_NAME,
    )


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    demo.launch()
