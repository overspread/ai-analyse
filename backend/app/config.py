from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    nvidia_api_key: str = ""
    chroma_persist_dir: str = "../chroma_db"
    database_url: str = "sqlite:///./dialysis.db"
    upload_dir: str = "./uploads"
    chunk_size: int = 220
    chunk_overlap: int = 30
    top_k: int = 5
    nvidia_llm_model: str = "minimaxai/minimax-m2.7"
    nvidia_embed_model: str = "nvidia/nv-embedqa-e5-v5"
    max_file_size_mb: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
