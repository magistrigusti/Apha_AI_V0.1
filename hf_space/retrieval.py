from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
import re
from typing import Iterable

from config import MAX_RETRIEVED_CHUNKS
from retrieval_jsonl import qa_chunks_from_jsonl
from retrieval_lexicon import (
    LONG_QUERY_HINTS,
    ROLE_HINT_TOKENS,
    SHORT_QUERY_HINTS,
    STOPWORDS,
)


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
# Монорепо: ../datasets. Только Space (корень = hf_space): hf_space/datasets/*.jsonl
DATASETS_DIR = BASE_DIR.parent / "datasets"
SPACE_DATASETS_DIR = BASE_DIR / "datasets"
# kb: .md/.txt/.jsonl; корень репо или hf_space/datasets: только *.jsonl (без дубля wp).
KB_SUFFIXES = {".md", ".txt", ".jsonl"}
CHUNK_SIZE = 1100
CHUNK_OVERLAP = 180
PRIMARY_SHORT_FILE = "allodium_wp_v2.jsonl"
PRIMARY_LONG_FILE = "ALLODIUM™м2.jsonl"
PRIMARY_SHORT_KEY = PRIMARY_SHORT_FILE.casefold()
PRIMARY_LONG_KEY = PRIMARY_LONG_FILE.casefold()
PRIMARY_DATASET_ORDER = (
    PRIMARY_SHORT_FILE,
    PRIMARY_LONG_FILE,
)


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1251"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _tokenize(text: str) -> list[str]:
    lowered = text.lower().replace("ё", "е")
    tokens = re.findall(r"[a-zа-я0-9]{3,}", lowered)
    return [token for token in tokens if token not in STOPWORDS]


def _chunk_text(text: str) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []

    if len(normalized) <= CHUNK_SIZE:
        return [_normalize_whitespace(normalized)]

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)

    while start < text_length:
        end = min(start + CHUNK_SIZE, text_length)
        candidate = normalized[start:end]

        if end < text_length:
            split_at = candidate.rfind("\n\n")
            if split_at < CHUNK_SIZE * 0.45:
                split_at = candidate.rfind(". ")
            if split_at < CHUNK_SIZE * 0.35:
                split_at = candidate.rfind(" ")
            if split_at > 0:
                end = start + split_at + 1
                candidate = normalized[start:end]

        cleaned = _normalize_whitespace(candidate)
        if cleaned:
            chunks.append(cleaned)

        if end >= text_length:
            break

        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def _iter_jsonl_files() -> Iterable[Path]:
    seen: set[Path] = set()

    # ========== СНАЧАЛА ГЛАВНЫЕ JSONL ИСТОЧНИКИ ==========
    for filename in PRIMARY_DATASET_ORDER:
        for base in (SPACE_DATASETS_DIR, DATASETS_DIR):
            path = base / filename
            if not path.exists():
                continue

            key = path.resolve()
            if key in seen:
                continue

            seen.add(key)
            yield path

    # ========== ПОТОМ ОСТАЛЬНЫЕ JSONL ==========
    for base in (SPACE_DATASETS_DIR, DATASETS_DIR):
        if not base.exists():
            continue

        for path in sorted(base.glob("*.jsonl")):
            key = path.resolve()
            if key in seen:
                continue

            seen.add(key)
            yield path


def _iter_knowledge_paths() -> Iterable[Path]:
    # ========== СНАЧАЛА DATASETS ==========
    yield from _iter_jsonl_files()

    # ========== ПОТОМ ВСПОМОГАТЕЛЬНЫЕ KNOWLEDGE_BASE ==========
    if KNOWLEDGE_DIR.exists():
        for path in sorted(KNOWLEDGE_DIR.rglob("*")):
            if path.is_file() and path.suffix.lower() in KB_SUFFIXES:
                yield path


def _append_chunk_records(
    chunks: list[dict[str, object]],
    path: Path,
    pieces: list[str],
    source_kind: str,
) -> None:
    title = path.stem.replace("_", " ").replace("-", " ").strip()
    relative = path.relative_to(BASE_DIR.parent).as_posix()

    for index, chunk in enumerate(pieces):
        tokens = _tokenize(chunk)
        if not tokens:
            continue

        chunks.append(
            {
                "source": relative,
                "source_kind": source_kind,
                "source_file": path.name.casefold(),
                "title": title or path.name,
                "chunk_index": index + 1,
                "text": chunk,
                "token_counts": Counter(tokens),
                "unique_tokens": set(tokens),
            }
        )


@lru_cache(maxsize=1)
def load_external_chunks() -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []

    for path in _iter_knowledge_paths():
        source_kind = (
            "knowledge_base" if KNOWLEDGE_DIR in path.parents else "datasets"
        )
        if path.suffix.lower() == ".jsonl":
            qa_chunks = qa_chunks_from_jsonl(path, _read_text)
            _append_chunk_records(chunks, path, qa_chunks, source_kind)
            continue

        text = _read_text(path).strip()
        if not text:
            continue
        _append_chunk_records(
            chunks, path, _chunk_text(text), source_kind
        )

    return chunks


def _query_has_hint(
    query_text: str,
    hints: tuple[str, ...],
) -> bool:
    return any(hint in query_text for hint in hints)


def _source_priority(chunk: dict[str, object]) -> int:
    source_file = str(chunk.get("source_file", ""))
    if source_file == PRIMARY_SHORT_KEY:
        return 3
    if source_file == PRIMARY_LONG_KEY:
        return 2
    if chunk.get("source_kind") == "knowledge_base":
        return 1
    return 0


def retrieve_knowledge(query: str, limit: int = MAX_RETRIEVED_CHUNKS) -> list[dict[str, object]]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_text = query.strip().lower().replace("ё", "е")
    query_counts = Counter(query_tokens)
    query_unique = set(query_tokens)
    role_query = bool(query_unique & ROLE_HINT_TOKENS)
    short_query = _query_has_hint(query_text, SHORT_QUERY_HINTS)
    long_query = _query_has_hint(query_text, LONG_QUERY_HINTS) or len(query_tokens) > 8
    ranked: list[tuple[float, dict[str, object]]] = []

    for chunk in load_external_chunks():
        overlap = query_unique & chunk["unique_tokens"]
        if not overlap:
            continue

        chunk_text = str(chunk["text"])
        normalized_chunk_text = chunk_text.lower().replace("ё", "е")
        score = 0.0
        for token in overlap:
            score += min(query_counts[token], chunk["token_counts"][token]) * 2.5

        score += (len(overlap) / max(len(query_unique), 1)) * 3

        if query_text and query_text in normalized_chunk_text:
            score += 2

        source_file = str(chunk.get("source_file", ""))

        # ========== КОРОТКИЙ КАНОНИЧНЫЙ ОТВЕТ ==========
        if source_file == PRIMARY_SHORT_KEY:
            score += 7.0
            if short_query:
                score += 3.0
            if len(chunk_text) < 900:
                score += 0.8

        # ========== ДЛИННЫЙ КАНОНИЧНЫЙ ОТВЕТ ==========
        elif source_file == PRIMARY_LONG_KEY:
            score += 5.0
            if long_query:
                score += 2.5
            if len(chunk_text) > 220:
                score += 1.0

        # ========== KNOWLEDGE_BASE — ВТОРИЧНЫЙ СЛОЙ ==========
        elif chunk["source_kind"] == "knowledge_base":
            score += 4.0 if role_query else 0.7

        else:
            score += 1.2

        if score > 0:
            ranked.append((score, chunk))

    ranked.sort(
        key=lambda item: (
            item[0],
            _source_priority(item[1]),
            len(item[1]["unique_tokens"]),
        ),
        reverse=True,
    )

    return [chunk for _, chunk in ranked[:limit]]


def build_retrieved_context(query: str) -> str:
    relevant_chunks = retrieve_knowledge(query)
    if not relevant_chunks:
        return ""

    blocks = []
    for chunk in relevant_chunks:
        header = (
            f"Source: {chunk['title']} "
            f"({chunk['source']}, chunk {chunk['chunk_index']})"
        )
        blocks.append(f"{header}\n{chunk['text']}")

    return "Confirmed reference context:\n\n" + "\n\n---\n\n".join(blocks)
