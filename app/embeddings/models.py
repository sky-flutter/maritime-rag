from dataclasses import dataclass
from app.chunking.models import Chunk


@dataclass(frozen=True)
class EmbeddedChunk:
    chunk: Chunk
    vector: list[float]
    embedding_model: str
