from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Document, ChatHistory
from app.schemas import ChatRequest, ChatResponse, SourceChunk, ChatHistoryResponse
from app.services.vector_store import search_chunks
from app.services.llm_service import answer_question

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not request.doc_ids:
        raise HTTPException(400, "At least one document ID is required")

    docs = db.query(Document).filter(Document.id.in_(request.doc_ids)).all()
    if not docs:
        raise HTTPException(404, "No valid documents found")

    chunks = search_chunks(request.question, doc_ids=request.doc_ids)

    if not chunks:
        return ChatResponse(answer="根据现有文档无法回答此问题，文档中未找到相关内容。", sources=[])

    answer = answer_question(request.question, chunks)

    sources = [
        SourceChunk(
            document_id=c["document_id"],
            document_name=next((d.original_filename for d in docs if d.id == c["document_id"]), "Unknown"),
            content=c["content"],
            score=round(c["score"], 4),
        )
        for c in chunks
    ]

    history = ChatHistory(
        question=request.question,
        answer=answer,
        source_doc_ids=request.doc_ids,
        source_chunks=[{"document_id": c["document_id"], "content": c["content"], "score": c["score"]} for c in chunks],
    )
    db.add(history)
    db.commit()

    return ChatResponse(answer=answer, sources=sources)


@router.get("/history", response_model=List[ChatHistoryResponse])
def list_history(db: Session = Depends(get_db)):
    return db.query(ChatHistory).order_by(ChatHistory.created_at.desc()).limit(100).all()
