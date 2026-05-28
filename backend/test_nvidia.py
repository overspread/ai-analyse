import os
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

try:
    print(f"Testing with model: nvidia/nv-embed-qa-4")
    embedder = NVIDIAEmbeddings(
        model="nvidia/nv-embed-qa-4",
        nvidia_api_key=api_key,
    )
    result = embedder.embed_query("Hello world")
    print(f"Success! Embedding length: {len(result)}")
except Exception as e:
    print(f"Failed with nvidia/nv-embed-qa-4: {e}")

try:
    print(f"\nTesting with model: nv-embed-qa-4")
    embedder = NVIDIAEmbeddings(
        model="nv-embed-qa-4",
        nvidia_api_key=api_key,
    )
    result = embedder.embed_query("Hello world")
    print(f"Success! Embedding length: {len(result)}")
except Exception as e:
    print(f"Failed with nv-embed-qa-4: {e}")

try:
    print(f"\nTesting with explicit base_url: https://integrate.api.nvidia.com/v1")
    embedder = NVIDIAEmbeddings(
        model="nvidia/nv-embed-qa-4",
        nvidia_api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    result = embedder.embed_query("Hello world")
    print(f"Success! Embedding length: {len(result)}")
except Exception as e:
    print(f"Failed with explicit base_url: {e}")
