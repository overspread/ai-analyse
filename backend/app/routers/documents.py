from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import aiofiles
import datetime
import os

from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse, DocumentListResponse
from app.config import settings
from app.services.document_parser import extract_text
from app.services.text_splitter import split_text
from app.services.vector_store import add_document_chunks, delete_document_chunks

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload", response_model=list[DocumentResponse])
async def upload_files(files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    results = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"Unsupported file type: {ext}")

        content = await file.read()
        file_size = len(content)
        if file_size > settings.max_file_size_mb * 1024 * 1024:
            raise HTTPException(400, f"File {file.filename} exceeds {settings.max_file_size_mb}MB limit")

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        stored_name = f"{timestamp}_{file.filename}"
        file_path = os.path.join(settings.upload_dir, stored_name)

        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            pages = extract_text(file_path)
            if not pages:
                raise HTTPException(400, f"Failed to extract text from {file.filename} - file may be empty or corrupted")
            
            chunks = split_text(pages, settings.chunk_size, settings.chunk_overlap)
            if not chunks:
                raise HTTPException(400, f"Failed to split text from {file.filename} into chunks")
            
            content_preview = chunks[0]["text"][:200] if chunks else pages[0]["text"][:200]

            doc = Document(
                filename=stored_name,
                original_filename=file.filename,
                file_path=file_path,
                file_type=ext[1:],
                file_size=file_size,
                chunk_count=len(chunks),
                content_preview=content_preview,
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            add_document_chunks(doc.id, chunks)

            results.append(doc)
        except Exception as e:
            db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(500, f"Failed to process {file.filename}: {str(e)}")
    return results


@router.get("", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    items = db.query(Document).order_by(Document.created_at.desc()).all()
    return {"total": len(items), "items": items}


@router.get("/{doc_id}/file")
def get_document_file(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(404, "File not found on disk")
    media_type = "application/pdf" if doc.file_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return FileResponse(doc.file_path, media_type=media_type, filename=doc.original_filename)


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    delete_document_chunks(doc_id)
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
