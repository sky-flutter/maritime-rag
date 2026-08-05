from app.embeddings.embedding_provider import EmbeddingProvider
from app.chunking.models import Chunk
from app.embeddings.models import EmbeddedChunk

class EmbeddingService:
    """Batches chunks and delegates to an EmbeddingProvider. Knows
    nothing about which provider is plugged in, or about the vector
    store that will eventually persist the results.
    """
    def __init__(self, provider: EmbeddingProvider, batch_size: int = 100) -> None:
        self._provider = provider
        self._batch_size = batch_size

    def embed_chunks(self, chunks: list[Chunk], limit: int | None = None) -> list[EmbeddedChunk]:
        chunks_to_embed = chunks[:limit] if limit is not None else chunks
        embedded: list[EmbeddedChunk] = []

        for start in range(0, len(chunks_to_embed), self._batch_size):
            batch = chunks_to_embed[start: start + self._batch_size]
            texts = [c.content for c in batch]
            vectors = self._provider.embed_batch(texts)

            embedded.extend(
                EmbeddedChunk(
                    chunk=chunk,
                    vector=vector,
                    embedding_model=self._provider.model
                )
                for chunk, vector in zip(batch, vectors)
            )

        return embedded