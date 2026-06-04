import os
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

try:
    embedder = NVIDIAEmbeddings(nvidia_api_key=api_key)
    models = embedder.available_models
    print("Available models:")
    for model in models:
        print(f"- {model.id} ({model.model_type})")
except Exception as e:
    print(f"Failed to list models: {e}")