from __future__ import annotations

from collections import Counter
from functools import lru_cache
from pathlib import Path
import re
from typing import Iterable

from config import MAX_RETRIEVED_CHUNKS
from retrieval_jsonl import qa_chunks_from_jsonl
from retrieval_lexicon import ROLE_HINT_TOKENS, STOPWORDS


BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
# Монорепо: ../datasets. Только Space (корень = hf_space): hf_space/datasets/*.jsonl
DATASETS_DIR = BASE_DIR.parent / "datasets"
SPACE_DATASETS_DIR = BASE_DIR / "datasets"
# kb: .md/.txt/.jsonl; корень репо или hf_space/datasets: только *.jsonl (без дубля wp).
KB_SUFFIXES = {".md", ".txt", ".jsonl"}
CHUNK_SIZE = 1100
CHUNK_OVERLAP = 180


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
    for base in (DATASETS_DIR, SPACE_DATASETS_DIR):
        if not base.exists():
            continue
        for path in sorted(base.glob("*.jsonl")):
            key = path.resolve()
            if key in seen:
                continue
            seen.add(key)
            yield path


def _iter_knowledge_paths() -> Iterable[Path]:
    if KNOWLEDGE_DIR.exists():
        for path in sorted(KNOWLEDGE_DIR.rglob("*")):
            if path.is_file() and path.suffix.lower() in KB_SUFFIXES:
                yield path
    yield from _iter_jsonl_files()


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


def retrieve_knowledge(query: str, limit: int = MAX_RETRIEVED_CHUNKS) -> list[dict[str, object]]:
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_counts = Counter(query_tokens)
    query_unique = set(query_tokens)
    role_query = bool(query_unique & ROLE_HINT_TOKENS)
    ranked: list[tuple[float, dict[str, object]]] = []

    for chunk in load_external_chunks():
        overlap = query_unique & chunk["unique_tokens"]
        if not overlap:
            continue

        score = 0.0
        for token in overlap:
            score += min(query_counts[token], chunk["token_counts"][token]) * 2.5

        score += (len(overlap) / max(len(query_unique), 1)) * 3

        if query.strip() and query.lower() in str(chunk["text"]).lower():
            score += 2

        if chunk["source_kind"] == "knowledge_base":
            score += 5 if role_query else 1.5

        if score > 0:
            ranked.append((score, chunk))

    ranked.sort(
        key=lambda item: (
            item[0],
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
