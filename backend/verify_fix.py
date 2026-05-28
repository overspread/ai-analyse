from app.services.vector_store import _get_embedding
from app.config import settings

def verify():
    print(f"Current model in settings: {settings.nvidia_embed_model}")
    try:
        embedding = _get_embedding()
        print(f"Embedding object: {embedding}")
        vec = embedding.embed_query("Verify fix")
        print(f"Successfully generated embedding. Length: {len(vec)}")
    except Exception as e:
        print(f"Verification failed: {e}")

if __name__ == "__main__":
    verify()
