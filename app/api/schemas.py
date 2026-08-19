from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str
    top_k: int = 5


class SourceResponse(BaseModel):
    chunk_id: str
    report_id: str
    section: str | None
    similarity_score: float


class QueryResponse(BaseModel):
    answer: str
    answered: bool
    source_ids: list[SourceResponse]
