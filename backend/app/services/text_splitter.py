import jieba
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict

jieba.initialize()


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
    return len(jieba.lcut(text))
