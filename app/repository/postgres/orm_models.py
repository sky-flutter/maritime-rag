from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReportDocumentORM(Base):
    """ORM mapping for the report_documents table. Internal to the
    repository layer — nothing outside `repository/` should import this.
    """
    __tablename__ = "reports_mda_json"

    report_id: Mapped[str] = mapped_column(primary_key=True)
    data_source: Mapped[str] = mapped_column(nullable=False)
    customer_name: Mapped[str] = mapped_column(nullable=False)
    imo: Mapped[int] = mapped_column(nullable=False)
    report_type: Mapped[str] = mapped_column(nullable=False)
    datetime_gmt: Mapped[datetime] = mapped_column(nullable=False)
    report_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    zn_updated_at: Mapped[datetime] = mapped_column(nullable=False)
