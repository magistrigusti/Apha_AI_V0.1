# ========================================
# app.py — Gradio UI для Альфы
# Точка входа HF Space
# ========================================

import gradio as gr
from model import reply


# ========== ИНТЕРФЕЙС ==========
with gr.Blocks(
    title="Альфа — Советник Аллода Зион"
) as demo:

    # ========== ЗАГОЛОВОК ==========
    gr.Markdown(
        "# Альфа — Советник Аллода Зион"
    )
    gr.Markdown(
        "Первый цифровой житель мира "
        "Allodium. Спроси о механиках, "
        "интерфейсе, лоре."
    )

    # ========== ЧАТ ==========
    # type="messages" — формат OpenAI-style
    chat = gr.Chatbot(
        height=420,
        type="messages",
    )

    # ========== ПОЛЕ ВВОДА ==========
    msg = gr.Textbox(
        label="Сообщение",
        placeholder="Спроси Альфу…",
    )

    # ========== КНОПКА ОЧИСТКИ ==========
    clear = gr.Button("Очистить диалог")

    # ========== ОБРАБОТЧИКИ ==========
    def user_send(user_message, chat_history):
        """Отправка сообщения от игрока"""
        chat_history.append({
            "role": "user",
            "content": user_message,
        })
        # Заглушка пока генерируется ответ
        chat_history.append({
            "role": "assistant",
            "content": "…",
        })
        return "", chat_history

    def bot_send(chat_history):
        """Генерация ответа Альфы"""
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

    # ========== СОБЫТИЯ ==========
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


# ========== ЗАПУСК ==========
if __name__ == "__main__":
    demo.launch()
