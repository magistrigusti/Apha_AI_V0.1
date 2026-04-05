# ========== JSONL Q&A для RAG ==========
from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path


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
        p, r = obj.get("prompt"), obj.get("response")
        if not p or not r:
            continue
        out.append(f"Вопрос: {p}\nОтвет: {r}")
    return out
