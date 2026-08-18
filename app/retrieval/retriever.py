from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from app.vectorstore.models import RetrievedChunk


@dataclass(frozen=True)
class RetrievalQuery:
    text: str
    top_k: int = 20
    metadata_filter: dict = field(default_factory=dict)
    datetime_from: datetime | None = None
    datetime_to: datetime | None = None


class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> list[RetrievedChunk]:
        raise NotImplementedError
