from __future__ import annotations

import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MAX_CHARS = 1150

DOCS = (
    {
        "source_id": "allodium_whitepaper_full",
        "title": "ALLODIUM™ White Paper",
        "filename_prefix": "ALLODIUM",
        "output": "allodium_source_chunks.jsonl",
        "base_keywords": (
            "allodium",
            "аллодиум",
            "аллод",
            "астрал",
            "лорд",
            "mercatus",
            "игра",
            "mmo",
            "rts",
            "rpg",
        ),
    },
    {
        "source_id": "dominum_whitepaper_full",
        "title": "Dominum™ White Paper",
        "filename": "dominum_whitepaper.txt",
        "output": "dominum_source_chunks.jsonl",
        "base_keywords": (
            "dominum",
            "dom",
            "dao",
            "крипто-республика",
            "остров",
            "чилийская патагоня",
            "nft-граждане",
            "governance",
            "allodium",
            "joker",
        ),
    },
)

HEADING_RE = re.compile(
    r"^(?:\d+(?:\.\d+)*\.|Этап\s+\d+\.|[A-ZА-ЯЁ][^.!?]{0,70}(?:White Paper|DAO|Advisors))\s*\S",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9™-]{3,}")


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    return path.read_text(encoding="utf-8", errors="ignore")


def find_source_path(config: dict[str, object]) -> Path:
    filename = config.get("filename")
    if isinstance(filename, str):
        path = BASE_DIR / filename
        if path.exists():
            return path

    prefix = str(config["filename_prefix"]).casefold()
    for path in sorted(BASE_DIR.glob("*.txt")):
        if path.name.casefold().startswith(prefix):
            return path

    raise FileNotFoundError(
        f"Source text for {config['title']} was not found"
    )


def clean_line(raw: str) -> str:
    line = raw.replace("\ufeff", "").strip()
    line = re.sub(r"\s+", " ", line)
    return line


def is_noise(line: str) -> bool:
    return (
        not line
        or line == "________________"
        or line.startswith("Вкладка ")
        or line in {"*", "* ________________"}
    )


def is_heading(line: str) -> bool:
    if line in {
        "ALLODIUM™",
        "White Paper",
        "Сказание об Астральном Расколе",
        "Dominum™ White Paper",
        "Crypto Republic & DAO",
    }:
        return True

    return bool(HEADING_RE.match(line)) and len(line) <= 130


def split_into_sections(text: str, fallback_title: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = fallback_title
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines
        body = "\n".join(current_lines).strip()
        if body:
            sections.append((current_title, current_lines))
        current_lines = []

    for raw in text.splitlines():
        line = clean_line(raw)
        if is_noise(line):
            continue

        if is_heading(line):
            flush()
            current_title = line
            continue

        current_lines.append(line)

    flush()
    return [(title, "\n".join(lines)) for title, lines in sections]


def split_body(body: str) -> list[str]:
    paragraphs = [part.strip() for part in body.splitlines() if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        next_len = current_len + len(paragraph) + 1
        if current and next_len > MAX_CHARS:
            chunks.append("\n".join(current).strip())
            current = []
            current_len = 0

        current.append(paragraph)
        current_len += len(paragraph) + 1

    if current:
        chunks.append("\n".join(current).strip())

    return chunks


def topic_hints(text: str, limit: int = 8) -> list[str]:
    stop = {
        "что",
        "это",
        "для",
        "как",
        "или",
        "при",
        "the",
        "and",
        "with",
    }
    hints: list[str] = []
    for token in TOKEN_RE.findall(text.lower().replace("ё", "е")):
        token = token.strip("-")
        if len(token) < 3 or token in stop or token in hints:
            continue
        hints.append(token)
        if len(hints) >= limit:
            break

    return hints


def build_row(
    config: dict[str, object],
    section: str,
    chunk: str,
    index: int,
) -> dict[str, object]:
    title = str(config["title"])
    source_id = str(config["source_id"])
    hints = topic_hints(f"{section}\n{chunk}")
    base_keywords = list(config["base_keywords"])
    aliases = [
        f"{title}: {section}",
        f"что сказано в разделе {section}",
        f"расскажи по white paper про {section}",
        f"объясни раздел {section}",
    ]

    if hints:
        aliases.extend(
            [
                f"что такое {hints[0]}",
                f"расскажи про {hints[0]}",
            ]
        )

    return {
        "prompt": f"{title}. Раздел: {section}. Фрагмент {index}.",
        "response": chunk,
        "aliases": aliases,
        "keywords": [source_id, section, *base_keywords, *hints],
        "source": source_id,
        "section": section,
        "chunk_index": index,
    }


def build_dataset(config: dict[str, object]) -> int:
    source_path = find_source_path(config)
    sections = split_into_sections(
        read_text(source_path),
        str(config["title"]),
    )
    rows: list[dict[str, object]] = []

    for section, body in sections:
        for index, chunk in enumerate(split_body(body), 1):
            rows.append(build_row(config, section, chunk, index))

    output_path = BASE_DIR / str(config["output"])
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for item in rows:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"written={len(rows)} -> {output_path.name}")
    return len(rows)


def main() -> None:
    total = 0
    for config in DOCS:
        total += build_dataset(config)

    print(f"total_source_rows={total}")


if __name__ == "__main__":
    main()
