from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column 
from sqlalchemy import JSON, String, Text, DateTime, func
from datetime import datetime
from pgvector.sqlalchemy import Vector

EMBEDDING_DIM = 1536

class VectorStoreBase(DeclarativeBase):
    pass

class ReportChunkORM(VectorStoreBase):
    __tablename__ = 'report_chunks'

    chunk_id: Mapped[str] = mapped_column(String, primary_key=True)
    report_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String, nullable=False)
    chunk_metadata: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())