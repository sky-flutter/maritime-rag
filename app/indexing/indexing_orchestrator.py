from datetime import datetime

from app.chunking.section_chunker import SectionChunker
from app.document_builder.document_builder import DocumentBuilder
from app.embeddings.embedding_service import EmbeddingService
from app.indexing.watermark_store import WatermarkStore
from app.repository.postgres.conn_manager import PostgresConnectionManager
from app.repository.postgres.orm_models import ReportDocumentORM
from app.repository.report_repository import ReportRepository
from app.vectorstore.vector_store import VectorStore
from sqlalchemy import select


class IndexingBatchError(Exception):
    def __init__(self, failed_report_id: str, cause: Exception) -> None:
        self.failed_report_id = failed_report_id
        self.cause = cause

        super().__init__(f"Batch failed for report: {failed_report_id}: {cause}")


class IndexingOrchestrator:
    def __init__(
        self,
        conn_manager: PostgresConnectionManager,
        watermark_store: WatermarkStore,
        report_repository: ReportRepository,
        document_builder: DocumentBuilder,
        chunker: SectionChunker,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self._conn_manager = conn_manager
        self._watermark_store = watermark_store
        self._report_repository = report_repository
        self._document_builder = document_builder
        self._chunker = chunker
        self._embedding_service = embedding_service
        self._vector_store = vector_store

    def _fetch_batch(self, watermark: datetime, batch_size: int):
        with self._conn_manager.session_scope() as session:
            stmt = select(ReportDocumentORM.report_id, ReportDocumentORM.updated_at)

            if watermark is not None:
                stmt = stmt.where(ReportDocumentORM.updated_at > watermark)

            stmt = stmt.order_by(ReportDocumentORM.updated_at.asc()).limit(batch_size)
            return session.execute(stmt).all()

    def _index_one(self, report_id: str):
        _report = self._report_repository.get_by_id(report_id)
        _document = self._document_builder.build(_report)
        _chunks = self._chunker.chunk(_document)
        _embedding_chunks = self._embedding_service.embed_chunks(_chunks)
        return self._vector_store.upsert(_embedding_chunks)

    def run(self, batch_size: int = 50) -> dict:
        watermark = self._watermark_store.get()
        batch = self._fetch_batch(watermark, batch_size)

        if not batch:
            return {
                "processed": 0,
                "watermark": watermark,
                "message": "No new/updated reports",
            }
        try:
            for report_id, _ in batch:
                self._index_one(report_id)
        except Exception as e:
            print(e)
            failed_report_id = report_id
            raise IndexingBatchError(failed_report_id, e) from e

        new_watermark = max(updated_at for _, updated_at in batch)

        self._watermark_store.advance(new_watermark)
        return {
            "processed": batch_size,
            "watermark": new_watermark,
            "report_ids": [r for r, _ in batch],
        }
