from config import MAX_CONTEXT_TURNS
from prompts import build_system_prompt


def build_messages(message, history):
    system_prompt = build_system_prompt(message)

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    limit = MAX_CONTEXT_TURNS * 2
    recent = history[-limit:]

    for msg in recent:
        messages.append(
            {
                "role": msg["role"],
                "content": msg["content"],
            }
        )

    messages.append({"role": "user", "content": message})
    return messages
