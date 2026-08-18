from app.embeddings.factory import get_openai_client
from app.llm.llm_service import LLMService
from app.llm.openai_llm_service import OpenAILLMService


def get_llm_service(model: str = "gpt-4o-mini") -> LLMService:
    return OpenAILLMService(client=get_openai_client(), model=model)
