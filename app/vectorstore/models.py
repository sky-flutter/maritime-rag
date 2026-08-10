from dataclasses import dataclass

@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    report_id: str
    content: str
    metadata: dict
    similarity_score: float