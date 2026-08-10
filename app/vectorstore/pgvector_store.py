from app.vectorstore.vector_store import VectorStore
from app.embeddings.models import EmbeddedChunk
from app.repository.postgres.conn_manager import PostgresConnectionManager
from sqlalchemy.dialects.postgresql import insert
from app.vectorstore.orm import ReportChunkORM
from app.vectorstore.models import RetrievedChunk
from sqlalchemy import text


class PgVectorStore(VectorStore):
    def __init__(self, connection_manager: PostgresConnectionManager) -> None:
        self._connection_manager = connection_manager

    def upsert(self, embedding_chunks: list[EmbeddedChunk]) -> None:
        if not embedding_chunks:
            return

        with self._connection_manager.session_scope() as session:
            rows = [
                {
                    "chunk_id": embedding.chunk.chunk_id,
                    "report_id": embedding.chunk.report_id,
                    "content": embedding.chunk.content,
                    "embedding": embedding.vector,
                    "embedding_model": embedding.embedding_model,
                    "chunk_metadata": embedding.chunk.metadata,
                }
                for embedding in embedding_chunks
            ]

            stmt = insert(ReportChunkORM).values(
                rows,
            )
            stmt.on_conflict_do_update(
                index_elements=["chunk_id"],
                set_={
                    "content": stmt.excluded.content,
                    "embedding": stmt.excluded.embedding,
                    "embedding_model": stmt.excluded.embedding_model,
                    "chunk_metadata": stmt.excluded.chunk_metadata,
                },
            )
            
            session.execute(stmt)

    def similarity_search(self, query_vector, top_k=5, metadata_filter=None):
        with self._connection_manager.session_scope() as session:
            vector_str = f"[{','.join(map(str, query_vector))}]"

            query = text(
                """
                SELECT chunk_id, report_id, content, chunk_metadata, 
                    1 - (embedding <=> :query_vector) as similarity
                FROM report_chunks
                ORDER BY embedding <=> :query_vector
                LIMIT :top_k
            """
            )

            results = (
                session
                .execute(query, {"query_vector": vector_str, "top_k": top_k})
                .mappings()
                .all()
            )

            return [
                RetrievedChunk(
                    chunk_id=row["chunk_id"],
                    content=row["content"],
                    report_id=row["report_id"],
                    metadata=row["metadata"],
                    similarity_score=row["similarityh"],
                )
                for row in results
            ]
