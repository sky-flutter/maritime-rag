from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReportDocumentORM(Base):
    """ORM mapping for the report_documents table. Internal to the
    repository layer — nothing outside `repository/` should import this.
    """
    __tablename__ = "report_documents"

    report_id: Mapped[str] = mapped_column(String, primary_key=True)
    data_source: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    imo: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    report_type: Mapped[str | None] = mapped_column(String, nullable=True)
    datetime_gmt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    record_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    operation_type: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
