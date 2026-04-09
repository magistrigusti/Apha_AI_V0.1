# ========== WHITE PAPER → JSONL ДЛЯ ALPHA (HF SPACE) ==========
# Читает ALLODIUM™м2.txt из этой же папки, пишет ALLODIUM™м2.jsonl.
# Много строк: на каждую строку текста — несколько уникальных вопросов,
# ответ всегда дословная цитата строки; порядок чередуется по ответам.

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from math import ceil


DIR = Path(__file__).resolve().parent
SRC = DIR / "ALLODIUM™м2.txt"
OUT = DIR / "ALLODIUM™м2.jsonl"
TARGET_LINES = 15000


def collect_rows(lines: list[str]) -> list[tuple[str, str, int]]:
    """Возвращает (response_line, section_short, line_no)."""
    section = "ALLODIUM™ White Paper"
    out: list[tuple[str, str, int]] = []
    heading_re = re.compile(r"^\d+(?:\.\d+)*\.\s*\S")

    for idx, raw in enumerate(lines, 1):
        line = raw.replace("\ufeff", "").strip()
        if not line or line == "________________" or line.startswith("Вкладка"):
            continue
        if heading_re.match(line):
            section = line[:72] + ("…" if len(line) > 72 else "")
            continue
        out.append((line, section, idx))
    return out


def topic_hints(text: str) -> list[str]:
    toks = re.findall(r"[A-Za-zА-Яа-яЁё0-9™]+(?:\s+[A-Za-zА-Яа-яЁё0-9™]+){0,3}", text)
    hints: list[str] = []
    for t in toks:
        t = t.strip()
        if len(t) < 3:
            continue
        if t not in hints:
            hints.append(t[:56])
        if len(hints) >= 6:
            break
    if not hints:
        hints = [text[:48].strip() + ("…" if len(text) > 48 else "")]
    return hints


def build_prompts(
    response: str,
    section: str,
    line_no: int,
    count: int,
    used: set[str],
) -> list[str]:
    hints = topic_hints(response)
    sec = section[:60]
    frames_ru = [
        "Игрок спрашивает про «{h}». Что сказать по white paper (раздел: {s})?",
        "Как в документе сформулировано про {h}? Контекст раздела: {s}.",
        "Нужна точная цитата из white paper про {h} ({s}).",
        "Кратко: что white paper говорит о {h}? Раздел «{s}».",
        "Ответь игроку, опираясь на white paper: тема {h}, блок «{s}».",
        "Есть ли в white paper строка про {h}? Укажи раздел «{s}».",
        "Про {h} — что написано в официальном тексте? ({s})",
        "Цитируй документ: тема {h}; ориентир раздела «{s}».",
    ]
    frames_en = [
        "According to the Allodium white paper ({s}), what is stated about {h}?",
        "Quote the white paper on {h} (section context: {s}).",
        "Player asks about {h}. What does the document say ({s})?",
    ]
    tails = [
        "",
        " Дай дословную строку.",
        " Только текст из документа, без пересказа.",
        " Ответ одной цитатой.",
    ]
    out: list[str] = []
    salt = 0
    while len(out) < count and salt < count * 20:
        fr = frames_ru[salt % len(frames_ru)]
        h = hints[(salt // 3) % len(hints)]
        s = sec
        base = fr.format(h=h, s=s) + tails[salt % len(tails)]
        if salt % 11 == 0:
            fe = frames_en[salt % len(frames_en)]
            base = fe.format(h=h, s=s)
        key = base.casefold()
        if key not in used:
            used.add(key)
            out.append(base)
        salt += 1
    if len(out) < count:
        # редкий запасной путь — уникальный хвост по номеру строки источника
        while len(out) < count:
            extra = f"[источник строка {line_no}] Уточни по white paper ({sec}): {hints[0]}?"
            if extra.casefold() not in used:
                used.add(extra.casefold())
                out.append(extra)
            else:
                extra = f"{extra} #{len(out)}"
                used.add(extra.casefold())
                out.append(extra)
    return out


def interleave(records: list[dict[str, str]]) -> list[dict[str, str]]:
    by_resp: dict[str, list[str]] = defaultdict(list)
    order: list[str] = []
    for r in records:
        resp = r["response"]
        if resp not in by_resp:
            order.append(resp)
        by_resp[resp].append(r["prompt"])
    out: list[dict[str, str]] = []
    while any(by_resp[k] for k in order):
        for resp in order:
            ps = by_resp[resp]
            if ps:
                out.append({"prompt": ps.pop(0), "response": resp})
    return out


def main() -> None:
    raw_lines = SRC.read_text(encoding="utf-8").splitlines()
    rows = collect_rows(raw_lines)
    if not rows:
        raise SystemExit("Нет строк для разбора в white paper.")

    n = len(rows)
    per = max(1, ceil(TARGET_LINES / n))
    used_prompts: set[str] = set()
    flat: list[dict[str, str]] = []

    for response, section, line_no in rows:
        prompts = build_prompts(response, section, line_no, per, used_prompts)
        for p in prompts:
            flat.append({"prompt": p, "response": response})

    flat = interleave(flat)
    if len(flat) > TARGET_LINES:
        flat = flat[:TARGET_LINES]

    with OUT.open("w", encoding="utf-8", newline="\n") as f:
        for row in flat:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"lines_in_txt={n} prompts_per_line~{per} written={len(flat)} -> {OUT}")


if __name__ == "__main__":
    main()
