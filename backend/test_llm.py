import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("NVIDIA_API_KEY")

try:
    print(f"Testing with model: meta/llama-3.1-70b-instruct")
    llm = ChatNVIDIA(
        model="meta/llama-3.1-70b-instruct",
        api_key=api_key,
    )
    result = llm.invoke("Hello, how are you?")
    print(f"Success! Response: {result.content}")
except Exception as e:
    print(f"Failed with meta/llama-3.1-70b-instruct: {e}")
