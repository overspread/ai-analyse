from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

SEPARATORS = ["\n\n", "\n", "。", "；", "，", " ", ""]
MAX_SAFE_CHARS = 240
DEFAULT_CHUNK_SIZE = 220
DEFAULT_CHUNK_OVERLAP = 30


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[str]:
    if not text or not text.strip():
        raise ValueError("Cannot split empty text")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be less than chunk_size")

    safe_chunk_size = min(chunk_size, DEFAULT_CHUNK_SIZE, MAX_SAFE_CHARS)
    safe_chunk_overlap = min(chunk_overlap, DEFAULT_CHUNK_OVERLAP, safe_chunk_size - 1)
    text_splitter = _build_splitter(safe_chunk_size, safe_chunk_overlap)
    chunks = text_splitter.split_text(text)
    if not chunks:
        raise ValueError("Text splitting produced no chunks")
    filtered_chunks = [c.strip() for c in chunks if c.strip()]
    if not filtered_chunks:
        raise ValueError("All chunks were empty after filtering")

    safe_chunks = []
    for chunk in filtered_chunks:
        safe_chunks.extend(_ensure_safe_chunk(chunk, safe_chunk_overlap))

    if not safe_chunks:
        raise ValueError("Text splitting produced no safe chunks")
    return safe_chunks


def _build_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=SEPARATORS,
        length_function=len,
    )


def _ensure_safe_chunk(text: str, chunk_overlap: int) -> List[str]:
    if len(text) <= MAX_SAFE_CHARS:
        return [text]

    fallback_overlap = min(chunk_overlap, 20)
    chunks = _build_splitter(MAX_SAFE_CHARS, fallback_overlap).split_text(text)
    filtered_chunks = [c.strip() for c in chunks if c.strip()]

    if not filtered_chunks:
        return []

    safe_chunks = []
    for chunk in filtered_chunks:
        if len(chunk) <= MAX_SAFE_CHARS:
            safe_chunks.append(chunk)
        else:
            safe_chunks.extend(_slice_by_chars(chunk, MAX_SAFE_CHARS, fallback_overlap))
    return safe_chunks


def _slice_by_chars(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    step = max(1, chunk_size - chunk_overlap)
    chunks = []
    start = 0

    while start < len(text):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
        start += step

    return chunks
