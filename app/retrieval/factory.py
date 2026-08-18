import os
from app.embeddings.factory import get_openai_client
from app.embeddings.openai_embedding_provider import OpenAIEmbeddingProvider
from app.repository.postgres.conn_manager import PostgresConnectionManager
from app.repository.config import POSTGRES_CONFIG
from app.retrieval.retriever import Retriever
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.query_analyzer import QueryAnalyzer
from app.retrieval.llm_query_analyzer import LLMQueryAnalyzer
from app.vectorstore.pgvector_store import PgVectorStore

_connection_manager: PostgresConnectionManager | None = None


def get_connection_manager() -> PostgresConnectionManager:
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = PostgresConnectionManager(
            POSTGRES_CONFIG, os.environ.get("DATABASE_URL", "")
        )

    return _connection_manager


def get_query_analyzer() -> QueryAnalyzer:
    return LLMQueryAnalyzer(client=get_openai_client())


def get_retriever(model: str = "text-embedding-3-small") -> Retriever:
    embedding_provider = OpenAIEmbeddingProvider(
        client=get_openai_client(), model=model
    )
    vector_store = PgVectorStore(get_connection_manager())
    return VectorRetriever(
        embedding_provider=embedding_provider, vector_store=vector_store
    )
