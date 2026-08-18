import os
from dotenv import load_dotenv
from sqlalchemy import select

from app.repository.postgres.conn_manager import PostgresConnectionManager
from app.repository.config import POSTGRES_CONFIG
from app.repository.report_repository import ReportRepository
from app.repository.postgres.orm_models import ReportDocumentORM
from app.document_builder.document_builder import DocumentBuilder
from app.chunking.section_chunker import SectionChunker
from app.chunking.token_counter import TiktokenCounter
from app.embeddings.factory import get_embedding_service, is_dry_run_enabled

load_dotenv()

LIMIT = 10  # number of reports to index in this run


def main() -> None:
    if is_dry_run_enabled():
        print("WARNING: EMBEDDING_DRY_RUN is enabled — only a few chunks "
              "total will be embedded across this whole run. Set "
              "EMBEDDING_DRY_RUN=false in .env for a real indexing run.\n")

    connection_manager = PostgresConnectionManager(POSTGRES_CONFIG, os.environ["DATABASE_URL"])
    report_repository = ReportRepository(connection_manager)
    document_builder = DocumentBuilder()
    chunker = SectionChunker(token_counter=TiktokenCounter())
    embedding_service = get_embedding_service()

    from app.vectorstore.pgvector_store import PgVectorStore
    vector_store = PgVectorStore(connection_manager)

    with connection_manager.session_scope() as session:
        report_ids = session.scalars(
            select(ReportDocumentORM.report_id).limit(LIMIT)
        ).all()

    print(f"Indexing {len(report_ids)} report(s)...\n")

    total_chunks = 0
    for report_id in report_ids:
        report = report_repository.get_by_id(report_id)
        document = document_builder.build(report)
        chunks = chunker.chunk(document)
        embedded_chunks = embedding_service.embed_chunks(chunks)
        vector_store.upsert(embedded_chunks)

        total_chunks += len(embedded_chunks)
        sections = [c.chunk.metadata.get("section") for c in embedded_chunks]
        print(f"  {report_id}: {len(embedded_chunks)} chunks -> {sections}")

    print(f"\nDone. Indexed {len(report_ids)} report(s), {total_chunks} chunk(s) total.")


if __name__ == "__main__":
    main()