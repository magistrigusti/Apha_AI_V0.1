
# ========================================
# model.py — Загрузка модели и генерация
# ========================================

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

from config import (
    MODEL_ID,
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P,
)
from chat import build_messages


# ========== ЗАГРУЗКА МОДЕЛИ ==========
print(f"[Alpha] Загружаем модель: {MODEL_ID}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_ID
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    device_map="auto",
)

print("[Alpha] Модель загружена!")


# ========== ГЕНЕРАЦИЯ ОТВЕТА ==========
def reply(message, history):
    """
    Генерируем ответ от модели.
    message  — текст от игрока
    history  — список пар [user, bot]
    """
    messages = build_messages(message, history)

    # Применяем шаблон чата модели
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    # Токенизируем
    inputs = tokenizer(
        [text],
        return_tensors="pt",
    ).to(model.device)

    # Генерируем
    output_ids = model.generate(
        **inputs,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
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