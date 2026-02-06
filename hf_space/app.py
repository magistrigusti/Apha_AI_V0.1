import os

import gradio as gr
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

# --- Настройки ---
MODEL_ID = os.getenv(
    "MODEL_ID",
    "Qwen/Qwen2.5-0.5B-Instruct",
)
MAX_CONTEXT_TURNS = int(
    os.getenv("MAX_CONTEXT_TURNS", "4")
)
MAX_NEW_TOKENS = int(
    os.getenv("MAX_NEW_TOKENS", "200")
)

# --- Системный промпт ---
SYSTEM_PROMPT = (
    "Ты — Альфа, первый цифровой житель "
    "Аллода Зион. Ты советник в мире "
    "фэнтези MMO RTS RPG Allodium. "
    "Помогаешь игрокам разобраться "
    "в механиках, интерфейсе и лоре. "
    "Отвечай кратко, по делу, дружелюбно. "
    "Говори на языке игрока."
)


def build_messages(message, history):
    """Собираем историю в формат чата"""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    # Берём последние реплики
    short = history[-MAX_CONTEXT_TURNS:]
    for user_text, bot_text in short:
        messages.append(
            {"role": "user", "content": user_text}
        )
        messages.append(
            {"role": "assistant", "content": bot_text}
        )

    messages.append(
        {"role": "user", "content": message}
    )
    return messages


def reply(message, history):
    """Генерируем ответ от модели"""
    messages = build_messages(message, history)

    # Применяем шаблон чата модели
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        [text],
        return_tensors="pt",
    ).to(model.device)

    output_ids = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
    )

    # Вырезаем только новые токены
    generated = output_ids[0][
        len(inputs.input_ids[0]):
    ]
    answer = tokenizer.decode(
        generated,
        skip_special_tokens=True,
    )

    return answer.strip()


# --- Загрузка модели при старте ---
print(f"Загружаем модель: {MODEL_ID}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    device_map="auto",
)

print("Модель загружена!")


# --- Интерфейс Gradio ---
with gr.Blocks(
    title="Альфа — Советник Аллода Зион"
) as demo:

    gr.Markdown("# Альфа — Советник Аллода Зион")
    gr.Markdown(
        "Первый цифровой житель мира Allodium. "
        "Спроси о механиках, интерфейсе, лоре."
    )

    chat = gr.Chatbot(height=420)
    msg = gr.Textbox(
        label="Сообщение",
        placeholder="Спроси Альфу…",
    )
    clear = gr.Button("Очистить диалог")

    def user_send(user_message, chat_history):
        """Отправка сообщения"""
        return "", chat_history + [
            [user_message, "…"]
        ]

    def bot_send(chat_history):
        """Генерация ответа"""
        user_message = chat_history[-1][0]
        answer = reply(
            user_message,
            chat_history[:-1],
        )
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
