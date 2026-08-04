from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Provider-agnostic contract for turning text into vectors.
    Concrete implementations (OpenAI, Cohere, local model) hide their
    SDK/API specifics behind this interface.
    """

    @abstractmethod
    def model(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Returns one vector per input text, in the same order."""
        raise NotImplementedError
