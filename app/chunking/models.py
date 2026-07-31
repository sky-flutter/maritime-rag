from dataclasses import dataclass, field


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    report_id: str
    content: str
    metadata: dict = field(default_factory=dict)