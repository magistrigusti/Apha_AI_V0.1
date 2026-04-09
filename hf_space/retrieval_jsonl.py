# ========== JSONL Q&A для RAG ==========
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path


def _pick_text(obj: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _pick_list(obj: dict[str, object], *keys: str) -> list[str]:
    for key in keys:
        value = obj.get(key)
        if not isinstance(value, list):
            continue

        out: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                out.append(text)

        if out:
            return out

    return []


def qa_chunks_from_jsonl(
    path: Path,
    read_text: Callable[[Path], str],
) -> list[str]:
    out: list[str] = []
    for line in read_text(path).splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        prompt = _pick_text(
            obj,
            "prompt",
            "question",
            "input",
        )
        response = _pick_text(
            obj,
            "response",
            "answer",
            "output",
        )
        keywords = _pick_list(
            obj,
            "keywords",
            "tags",
            "aliases",
        )

        if not prompt or not response:
            continue

        parts = [
            f"Вопрос: {prompt}",
            f"Ответ: {response}",
        ]
        if keywords:
            parts.append(
                "Ключевые слова: " + ", ".join(keywords)
            )

        out.append("\n".join(parts))

    return out
