from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.vectorstore.models import RetrievedChunk


@dataclass(frozen=True)
class PromptResult:
    system_prompt: str
    user_prompt: str
    response_schema: dict
    source_map: dict[str, RetrievedChunk]


class PromptBuilder(ABC):
    @abstractmethod
    def build(self, question: str, chunks: list[RetrievedChunk]) -> PromptResult:
        raise NotImplementedError
