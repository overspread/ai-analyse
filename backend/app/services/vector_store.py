import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.config import settings as app_settings

_embedding = None
_client = None
_collection = None

BATCH_SIZE = 50
MAX_WORKERS = 5


class MockEmbeddings:
    def embed_documents(self, texts):
        return [[0.1] * 1024 for _ in texts]
    def embed_query(self, text):
        return [0.1] * 1024

def _get_embedding():
    global _embedding
    if _embedding is None:
        if not app_settings.nvidia_api_key:
            print("[Embedding] No API key configured, using mock embeddings")
            _embedding = MockEmbeddings()
        else:
            _embedding = NVIDIAEmbeddings(
                model=app_settings.nvidia_embed_model,
                api_key=app_settings.nvidia_api_key,
            )
    return _embedding


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=app_settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        _collection = _client.get_or_create_collection(
            name="analyse_docs",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_document_chunks(
    doc_id: int,
    chunks: List[dict],
    metadata: Optional[List[dict]] = None,
    progress_callback=None,
):
    if doc_id <= 0:
        raise ValueError("doc_id must be positive")
    if not chunks:
        raise ValueError("chunks cannot be empty")
    if not all(isinstance(chunk, dict) and "text" in chunk for chunk in chunks):
        raise ValueError("chunks must be dicts with 'text' key")
    if not all(chunk["text"].strip() for chunk in chunks):
        raise ValueError("all chunks must have non-empty text")
    
    collection = _get_collection()
    embedding = _get_embedding()
    
    if metadata:
        metadatas = metadata
    else:
        metadatas = [
            {"document_id": doc_id, "chunk_index": i, "page_number": c.get("page_number", 1)}
            for i, c in enumerate(chunks)
        ]
    
    total = len(chunks)
    batches = []
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        batches.append({
            "texts": [c["text"] for c in batch],
            "ids": [f"doc{doc_id}_chunk{j}" for j in range(i, i + len(batch))],
            "metadatas": metadatas[i:i + BATCH_SIZE],
            "idx": i,
        })
    
    completed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for b in batches:
            future = executor.submit(_embed_batch, embedding, b["texts"], b["ids"], b["metadatas"], collection)
            futures[future] = b
        
        for future in as_completed(futures):
            exc = future.exception()
            if exc:
                raise ValueError(f"Failed to embed batch: {exc}")
            completed += 1
            if progress_callback:
                pct = int((completed / len(batches)) * 100)
                progress_callback(pct)


def search_chunks(query: str, doc_ids: Optional[List[int]] = None, top_k: int = 5):
    collection = _get_collection()
    embedding = _get_embedding()

    query_vector = embedding.embed_query(query)

    where_filter = None
    if doc_ids:
        where_filter = {"document_id": {"$in": doc_ids}}

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    if results["ids"] and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            retrieved.append({
                "id": results["ids"][0][i],
                "document_id": results["metadatas"][0][i].get("document_id"),
                "page_number": results["metadatas"][0][i].get("page_number"),
                "content": results["documents"][0][i],
                "score": 1 - results["distances"][0][i],
            })
    return retrieved


def delete_document_chunks(doc_id: int):
    collection = _get_collection()
    collection.delete(where={"document_id": doc_id})


def _embed_batch(embedding, texts, ids, metadatas, collection):
    vectors = embedding.embed_documents(texts)
    if not vectors or len(vectors) != len(texts):
        raise ValueError("Failed to generate embeddings for batch")
    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )
