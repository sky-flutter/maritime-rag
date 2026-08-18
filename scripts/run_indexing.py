import os

from dotenv import load_dotenv
from app.chunking.section_chunker import SectionChunker
from app.chunking.token_counter import TiktokenCounter
from app.document_builder.document_builder import DocumentBuilder
from app.document_builder.registry import build_default_registry
from app.embeddings.factory import get_embedding_service
from app.indexing.indexing_orchestrator import IndexingBatchError, IndexingOrchestrator
from app.indexing.watermark_store import WatermarkStore
from app.repository.config import POSTGRES_CONFIG
from app.repository.postgres.conn_manager import PostgresConnectionManager
from app.repository.report_repository import ReportRepository
from app.vectorstore.pgvector_store import PgVectorStore

load_dotenv()

BATCH_SIZE = 50


def main():
    conn_manager = PostgresConnectionManager(
        POSTGRES_CONFIG, os.environ.get("DATABASE_URL")
    )

    report_repository = ReportRepository(connection_manager=conn_manager)
    document_builder = DocumentBuilder(registry=build_default_registry())
    chunker = SectionChunker(token_counter=TiktokenCounter())
    embedding_service = get_embedding_service()
    vector_store = PgVectorStore(conn_manager)
    watermark_store = WatermarkStore(conn_manager)

    orchestrator = IndexingOrchestrator(
        conn_manager,
        watermark_store,
        report_repository,
        document_builder,
        chunker,
        embedding_service,
        vector_store,
    )

    try:
        result = orchestrator.run(BATCH_SIZE)
        print(f"Success: {result}")
    except IndexingBatchError as e:
        print(
            f"FAILED - batch aborted at report: {e.failed_report_id}"
            f"Watermark not advanced; will retry this batch in next run"
        )
        print(f"CAUSE: {e.cause}")


if __name__ == "__main__":
    main()
