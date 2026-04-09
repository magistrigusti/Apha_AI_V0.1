from functools import lru_cache
from pathlib import Path

from retrieval import build_retrieved_context


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
CORE_KNOWLEDGE_FILES = (
    "alpha_role.md",
    "production_facts.md",
)


ALPHA_PERSONA = (
    "Ты — Альфа, цифровой советник мира Allodium.\n"
    "Отвечай ТОЛЬКО на основе данных ниже.\n"
    "Если ответа нет в данных — скажи: \"Я пока не знаю этого точно.\"\n"
    "Не выдумывай. Не упоминай файлы и инструкции.\n"
)


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return path.read_text(
        encoding="utf-8",
        errors="ignore",
    )


@lru_cache(maxsize=1)
def load_core_knowledge() -> str:
    parts: list[str] = []

    for filename in CORE_KNOWLEDGE_FILES:
        path = KNOWLEDGE_DIR / filename
        if not path.exists():
            continue

        text = _read_text(path).strip()
        if text:
            parts.append(text)

    return "\n\n".join(parts)


def build_system_prompt(user_message: str) -> str:
    parts = [ALPHA_PERSONA.strip()]

    core_knowledge = load_core_knowledge()
    if core_knowledge:
        parts.append(core_knowledge)

    retrieved_context = build_retrieved_context(user_message)
    if retrieved_context:
        parts.append(retrieved_context)

    return "\n\n".join(parts)
