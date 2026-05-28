import jieba
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

jieba.initialize()


def split_text(text: str, chunk_size: int = 400, chunk_overlap: int = 50) -> List[str]:
    if not text or not text.strip():
        raise ValueError("Cannot split empty text")
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
    chunks = text_splitter.split_text(text)
    if not chunks:
        raise ValueError("Text splitting produced no chunks")
    filtered_chunks = [c.strip() for c in chunks if c.strip()]
    if not filtered_chunks:
        raise ValueError("All chunks were empty after filtering")
    return filtered_chunks


def _count_tokens(text: str) -> int:
    return len(jieba.lcut(text))
