from app.llm.factory import get_llm_service
from app.llm.openai_llm_service import OpenAILLMService
from app.prompt.grounded_prompt_builder import GroundedPromptBuilder
from app.retrieval.factory import get_query_analyzer, get_retriever
from app.retrieval.query_analyzer import QueryAnalyzer
from app.retrieval.retriever import Retriever


def get_query_analyzer_dep() -> QueryAnalyzer:
    return get_query_analyzer()


def get_retriever_dep() -> Retriever:
    return get_retriever()


def get_prompt_builder_dep() -> GroundedPromptBuilder:
    return GroundedPromptBuilder()


def get_llm_service_dep() -> OpenAILLMService:
    return get_llm_service()
