import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from typing import List, Optional
from app.config import settings as app_settings

_embedding = None
_client = None
_collection = None


def _get_embedding() -> NVIDIAEmbeddings:
    global _embedding
    if _embedding is None:
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
            name="dialysis_docs",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_document_chunks(
    doc_id: int,
    chunks: List[str],
    metadata: Optional[List[dict]] = None,
):
    if not chunks:
        return
    collection = _get_collection()
    embedding = _get_embedding()
    ids = [f"doc{doc_id}_chunk{i}" for i in range(len(chunks))]
    metadatas = metadata or [{"document_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    vectors = embedding.embed_documents(chunks)
    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=chunks,
        metadatas=metadatas,
    )


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
                "content": results["documents"][0][i],
                "score": 1 - results["distances"][0][i],
            })
    return retrieved


def delete_document_chunks(doc_id: int):
    collection = _get_collection()
    collection.delete(where={"document_id": doc_id})
