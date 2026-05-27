import jieba
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

jieba.initialize()


def split_text(text: str, chunk_size: int = 400, chunk_overlap: int = 50) -> List[str]:
    separators = ["\n\n", "\n", "。", "；", "，", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=_count_tokens,
    )
    chunks = text_splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]


def _count_tokens(text: str) -> int:
    return len(jieba.lcut(text))
