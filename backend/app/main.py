from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db, SessionLocal
from app.routers import documents, chat
from app.models import UploadTask
import datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        stale = db.query(UploadTask).filter(
            UploadTask.status.in_(["processing", "parsing"]),
            UploadTask.updated_at < cutoff,
        ).all()
        for t in stale:
            t.status = "failed"
            t.error_message = "服务重启，任务已中断"
            t.stage = "已中断"
        if stale:
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title="AI Dialysis Assistant", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "AI Dialysis Assistant API is running"}
