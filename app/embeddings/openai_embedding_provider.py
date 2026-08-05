import time
from openai import OpenAI, OpenAIError
from app.embeddings.embedding_provider import EmbeddingProvider


class EmbeddingProviderException(Exception):

    def __init__(self, message: str, failed_count: int) -> None:
        self.failed_count = failed_count
        super().__init__(message)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        client: OpenAI,
        model: str = 'text-embedding-3-small',
        max_retries: int = 3,
        backoff_seconds: float = 1.0
    )-> None:
        self._client = client
        self._model = model
        self._max_retries = max_retries
        self._backoff_seconds = backoff_seconds


    @property
    def model(self) -> str:
        return self._model

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        last_error: Exception | None = None  
        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._client.embeddings.create(input=texts, model=self._model)
                return [item.embedding for item in response.data] 
            except OpenAIError as e:
                last_error = e
                if attempt < self._max_retries:
                    time.sleep(self._backoff_seconds * attempt)

        return EmbeddingProviderException(
            f'Failed to embed batch of {len(texts)} texts after '
            f'{self._max_retries} attemps: {last_error}' ,
            failed_count=len(texts)
        )