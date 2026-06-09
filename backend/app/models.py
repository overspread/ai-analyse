import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), index=True, nullable=True)
    chunk_count = Column(Integer, default=0)
    content_preview = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_doc_ids = Column(JSON, default=list)
    source_chunks = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class UploadTask(Base):
    __tablename__ = "upload_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), default="")
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    stage = Column(String(50), default="")
    doc_id = Column(Integer, nullable=True)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
