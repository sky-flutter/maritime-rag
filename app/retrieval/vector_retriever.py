from app.embeddings.embedding_provider import EmbeddingProvider
from app.retrieval.retriever import RetrievalQuery, Retriever
from app.vectorstore.models import RetrievedChunk
from app.vectorstore.vector_store import VectorStore


class VectorRetriever(Retriever):
    """Embeds the query text and delegates the actual search to a
    VectorStore. Depends on EmbeddingProvider directly (not
    EmbeddingService) since it only ever embeds one query at a time —
    it has no need for the service's batching machinery.
    """
    
    def __init__(
        self, embedding_provider: EmbeddingProvider, vector_store: VectorStore
    ):
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def _embed_query(self, text: str) -> list[float]:
        return self._embedding_provider.embed_batch([text])[0]

    def retrieve(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        query_vector = self._embed_query(query.text)
        return self._vector_store.similarity_search(
            query_vector=query_vector,
            top_k=query.top_k,
            metadata_filter=query.metadata_filter,
            datetime_from=query.datetime_from,
            datetime_to=query.datetime_to
        )
