from langchain_nvidia_ai_endpoints import ChatNVIDIA
from typing import List
from app.config import settings

_llm = None


class MockLLM:
    def invoke(self, prompt: str):
        class MockResponse:
            def __init__(self):
                self.content = "这是一个测试回答。由于未配置有效的 NVIDIA API Key，当前使用模拟模式。"
        return MockResponse()

SYSTEM_PROMPT = """你是一个专业的文档分析助手。
请严格基于以下提供的文档内容来回答用户的问题。
如果你无法从文档中找到答案，请明确说明"根据现有文档无法回答此问题"。
在回答中适当引用文档原文作为依据。

【参考文档内容】
{context}

【用户问题】
{question}"""

DISCLAIMER = "\n\n---\n*以上信息基于文档内容生成，仅供参考。*"


def _get_llm():
    global _llm
    if _llm is None:
        if not settings.nvidia_api_key:
            print("[LLM] No API key configured, using mock LLM")
            _llm = MockLLM()
        else:
            _llm = ChatNVIDIA(
                model=settings.nvidia_llm_model,
                api_key=settings.nvidia_api_key,
                temperature=0.3,
                max_tokens=2048,
            )
    return _llm


def answer_question(question: str, context_chunks: List[dict]) -> str:
    llm = _get_llm()
    context = "\n\n".join(
        f"[来源 {i + 1}]: {c['content']}" for i, c in enumerate(context_chunks)
    )
    prompt = SYSTEM_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt)
    return response.content + DISCLAIMER
