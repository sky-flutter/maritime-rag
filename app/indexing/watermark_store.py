from datetime import datetime
from app.repository.postgres.conn_manager import PostgresConnectionManager
from app.indexing.orm_models import IndexingWatermarkORM
from sqlalchemy.dialects.postgresql import insert

WATERMARK_ID = "default"


class WatermarkStore:
    def __init__(self, conn_manager: PostgresConnectionManager):
        self._conn_manager = conn_manager

    def get(self) -> datetime | None:
        with self._conn_manager.session_scope() as session:
            row = session.get(IndexingWatermarkORM, WATERMARK_ID)
            return row.last_processed_updated_at if row else None

    def advance(self, new_watermark: datetime) -> None:
        with self._conn_manager.session_scope() as session:
            stmt = insert(IndexingWatermarkORM).values(
                id=WATERMARK_ID, last_processed_updated_at=new_watermark
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "last_processed_updated_at": stmt.excluded.last_processed_updated_at
                },
            )

            session.execute(stmt)
