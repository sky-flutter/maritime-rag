from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field


@dataclass(frozen=True)
class QueryAnalysis:
    original_text: str
    metadata_filter: dict = field(default_factory=dict)
    datetime_from: datetime | None = None
    datetime_to: datetime | None = None


class QueryAnalyzer(ABC):
    @abstractmethod
    def analyze(self, text: str) -> QueryAnalysis:
        raise NotImplementedError
