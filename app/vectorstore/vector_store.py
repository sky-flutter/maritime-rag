from datetime import datetime
from app.embeddings.models import EmbeddedChunk
from abc import ABC, abstractmethod
from app.vectorstore.models import RetrievedChunk


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, embedding_chunks: list[EmbeddedChunk]) -> None:
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        metadata_filter: dict | None = None,
        datetime_from: datetime | None = None,
        datetime_to: datetime | None = None,
    ) -> list[RetrievedChunk]:
        raise NotImplementedError
