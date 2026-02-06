import os

import gradio as gr
from transformers import pipeline


MODEL_ID = os.getenv("MODEL_ID", "microsoft/DialoGPT-small")
MAX_CONTEXT_TURNS = int(os.getenv("MAX_CONTEXT_TURNS", "4"))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "120"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

SYSTEM_PROMPT = (
    "Ты — первый житель Аллода Зион. "
    "Ты цифровой агент, спокойный и "
    "вдумчивый. Отвечай кратко, "
    "по делу, на русском."
)


def build_prompt(message, history):
    # Собираем контекст из последних реплик
    lines = [SYSTEM_PROMPT]
    short_history = history[-MAX_CONTEXT_TURNS:]
    for user_text, bot_text in short_history:
        lines.append(f"Пользователь: {user_text}")
        lines.append(f"Агент: {bot_text}")
    lines.append(f"Пользователь: {message}")
    lines.append("Агент:")
    return "\n".join(lines)


def trim_answer(text):
    # Срезаем лишнее после первой пустой строки
    parts = text.strip().split("\n\n")
    return parts[0].strip()


def reply(message, history):
    prompt = build_prompt(message, history)
    result = generator(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        do_sample=True,
        eos_token_id=generator.tokenizer.eos_token_id,
    )

    full_text = result[0]["generated_text"]
    if full_text.startswith(prompt):
        answer = full_text[len(prompt):].strip()
    else:
        answer = full_text.strip()

    answer = trim_answer(answer)
    return answer


# Загружаем модель один раз при старте Space
generator = pipeline(
    "text-generation",
    model=MODEL_ID,
)


with gr.Blocks() as demo:
    gr.Markdown("# Аллод Зион — Первый Житель")
    gr.Markdown(
        "Минимальный агент на бесплатном HF Space. "
        "Модель можно заменить через MODEL_ID."
    )

    chat = gr.Chatbot(height=420)
    msg = gr.Textbox(
        label="Сообщение",
        placeholder="Напиши вопрос первому жителю…",
    )
    clear = gr.Button("Очистить диалог")

    def user_send(user_message, chat_history):
        return "", chat_history + [[user_message, "…"]]

    def bot_send(chat_history):
        user_message = chat_history[-1][0]
        answer = reply(user_message, chat_history[:-1])
        chat_history[-1][1] = answer
        return chat_history

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


if __name__ == "__main__":
    demo.launch()
