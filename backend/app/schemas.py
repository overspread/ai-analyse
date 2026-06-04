import datetime
from pydantic import BaseModel, Field
from typing import Optional, List


class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_size: int
    chunk_count: int
    content_preview: str
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total: int
    items: list[DocumentResponse]


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    doc_ids: list[int]


class SourceChunk(BaseModel):
    document_id: int
    document_name: str
    content: str
    score: float
    page_number: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]


class ChatHistoryResponse(BaseModel):
    id: int
    question: str
    answer: str
    source_doc_ids: list[int]
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
