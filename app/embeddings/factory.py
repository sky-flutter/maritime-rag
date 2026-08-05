import os
from dotenv import load_dotenv
from app.embeddings.openai_embedding_provider  import OpenAIEmbeddingProvider
from app.embeddings.embedding_service import EmbeddingService
from openai import OpenAI

load_dotenv()
_openai_client: OpenAI | None = None 

def get_openai_client() -> OpenAI:
    global _openai_client 
    if _openai_client is None:
        api_key = os.environ.get('OPENAI_API_KEY', '')
        _openai_client = OpenAI(api_key=api_key)

    return _openai_client

def get_embedding_service(model: str = 'text-embedding-3-small'):
    provider = OpenAIEmbeddingProvider(
        client=get_openai_client(),
        model=model,
    )

    return EmbeddingService(provider=provider)

def is_dry_run_enabled() -> bool:
    return os.environ.get('EMBEDDING_DRY_RUN', 'false').lower() == 'true'

def get_dry_run_limit() -> int:
    return int(os.environ.get('EMBEDDING_DRY_RUN_LIMIT', '2'))

