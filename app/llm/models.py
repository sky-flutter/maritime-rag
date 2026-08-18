from dataclasses import dataclass, field

from app.vectorstore.models import RetrievedChunk


@dataclass(frozen=True)
class Answer:
    answered: bool
    text: str
    sources: list[RetrievedChunk] = field(default_factory=list)
