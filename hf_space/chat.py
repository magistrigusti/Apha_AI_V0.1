# ========================================
# chat.py — Сборка истории сообщений
# Формат: OpenAI-style messages
# ========================================

from config import MAX_CONTEXT_TURNS
from prompts import SYSTEM_PROMPT


def build_messages(message, history):
    """
    Собираем историю в формат чата.
    history — список словарей:
    [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."},
    ]
    Берём только последние реплики
    чтобы не переполнять контекст.
    """
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # Берём последние N пар
    # (каждая пара = 2 сообщения)
    limit = MAX_CONTEXT_TURNS * 2
    recent = history[-limit:]

    for msg in recent:
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
        })

    # Новое сообщение от игрока
    messages.append(
        {"role": "user", "content": message}
    )

    return messages
