from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, func


class IndexingBase(DeclarativeBase):
    pass


class IndexingWatermarkORM(IndexingBase):
    __tablename__ = "indexing_watermark"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    last_processed_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
