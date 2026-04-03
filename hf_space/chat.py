from config import MAX_CONTEXT_TURNS
from prompts import build_system_prompt


def _content_to_text(content: object) -> str:
    # Gradio 6 может вернуть content не строкой,
    # а списком/словарем с текстовыми блоками.
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []

        for item in content:
            text = _content_to_text(item)
            if text:
                parts.append(text)

        return "\n".join(parts).strip()

    if isinstance(content, dict):
        for key in (
            "text",
            "value",
            "content",
            "path",
            "url",
            "orig_name",
        ):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        return ""

    return ""


def build_messages(message, history):
    message_text = _content_to_text(message)
    system_prompt = build_system_prompt(message_text)

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    limit = MAX_CONTEXT_TURNS * 2
    recent = history[-limit:]

    for msg in recent:
        if not isinstance(msg, dict):
            continue

        role = msg.get("role")
        if role not in {"user", "assistant", "system"}:
            continue

        content = _content_to_text(msg.get("content"))
        if not content:
            continue

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    messages.append({"role": "user", "content": message_text})
    return messages
