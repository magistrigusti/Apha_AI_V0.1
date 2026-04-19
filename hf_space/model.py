
# ========================================
# model.py — Загрузка модели и генерация
# ========================================

from config import (
    ALPHA_MODEL_PROVIDER,
    MODEL_ID,
    MAX_NEW_TOKENS,
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_MODEL,
    TEMPERATURE,
    TOP_P,
)
from chat import build_messages
from texts import (
    MODEL_LOADED_MESSAGE,
    MODEL_LOADING_TEMPLATE,
)


USE_NVIDIA_API = ALPHA_MODEL_PROVIDER in {
    "nvidia",
    "nvidia-api",
    "nim",
}

tokenizer = None
model = None
nvidia_client = None


def _load_local_model():
    global model, tokenizer

    if model is not None and tokenizer is not None:
        return

    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
    )

    print(MODEL_LOADING_TEMPLATE.format(model_id=MODEL_ID))

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype="auto",
        device_map="auto",
    )

    print(MODEL_LOADED_MESSAGE)


def _load_nvidia_client():
    global nvidia_client

    if nvidia_client is not None:
        return nvidia_client

    if not NVIDIA_API_KEY:
        raise RuntimeError(
            "NVIDIA_API_KEY is required when ALPHA_MODEL_PROVIDER=nvidia"
        )

    from openai import OpenAI

    print(f"[Alpha] Using NVIDIA API model: {NVIDIA_MODEL}")
    nvidia_client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=NVIDIA_API_KEY,
    )
    return nvidia_client


if USE_NVIDIA_API:
    _load_nvidia_client()
else:
    _load_local_model()


# ========== ГЕНЕРАЦИЯ ОТВЕТА ==========
def reply(message, history):
    """
    Генерируем ответ от модели.
    message  — текст от игрока
    history  — список пар [user, bot]
    """
    messages = build_messages(message, history)

    if USE_NVIDIA_API:
        response = _load_nvidia_client().chat.completions.create(
            model=NVIDIA_MODEL,
            messages=messages,
            max_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        content = response.choices[0].message.content or ""
        return content.strip()

    _load_local_model()

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
