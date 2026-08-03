from abc import ABC, abstractmethod
from app.chunking.models import Chunk
from app.document_builder.models import Document


class Chunker(ABC):
    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        raise NotImplementedError
