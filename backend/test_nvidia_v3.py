import os
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

try:
    print(f"Testing with model: nvidia/nv-embedqa-e5-v5")
    embedder = NVIDIAEmbeddings(
        model="nvidia/nv-embedqa-e5-v5",
        nvidia_api_key=api_key,
    )
    result = embedder.embed_query("Hello world")
    print(f"Success! Embedding length: {len(result)}")
except Exception as e:
    print(f"Failed with nvidia/nv-embedqa-e5-v5: {e}")
