from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict

SEPARATORS = ["\n\n", "\n", "。", "；", "，", " ", ""]
MAX_SAFE_CHARS = 240
DEFAULT_CHUNK_SIZE = 220
DEFAULT_CHUNK_OVERLAP = 30


def split_text(pages: List[Dict], chunk_size: int = 400, chunk_overlap: int = 50) -> List[Dict]:
    if not pages:
        raise ValueError("Cannot split empty pages")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be non-negative")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be less than chunk_size")
    
    separators = ["\n\n", "\n", "。", "；", "，", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=_count_tokens,
    )
    
    result = []
    for page in pages:
        page_number = page["page_number"]
        text = page["text"]
        if not text or not text.strip():
            continue
        page_chunks = text_splitter.split_text(text)
        for chunk in page_chunks:
            stripped = chunk.strip()
            if stripped:
                result.append({
                    "page_number": page_number,
                    "text": stripped,
                })
    
    if not result:
        raise ValueError("All chunks were empty after filtering")
    return result


def _count_tokens(text: str) -> int:
    return len(text)


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
