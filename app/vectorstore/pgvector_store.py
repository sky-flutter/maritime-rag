from app.vectorstore.vector_store import VectorStore
from app.embeddings.models import EmbeddedChunk
from app.repository.postgres.conn_manager import PostgresConnectionManager
from sqlalchemy.dialects.postgresql import insert
from app.vectorstore.orm import ReportChunkORM
from app.vectorstore.models import RetrievedChunk
from sqlalchemy import text
from datetime import datetime


class PgVectorStore(VectorStore):
    def __init__(self, connection_manager: PostgresConnectionManager) -> None:
        self._connection_manager = connection_manager

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        cleaned = value.strip().rstrip("Z").strip()
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
        return None

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
                    "report_datetime_gmt": self._parse_datetime(
                        embedding.chunk.metadata.get("datetime_gmt")
                    ),
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

    def similarity_search(
        self,
        query_vector,
        top_k=5,
        metadata_filter=None,
        datetime_from: datetime | None = None,
        datetime_to: datetime | None = None,
    ):
        with self._connection_manager.session_scope() as session:
            vector_str = f"[{','.join(map(str, query_vector))}]"

            where_clauses = []
            params = {"query_vector": vector_str, "top_k": top_k}
            if metadata_filter:
                for i, (key, value) in enumerate(metadata_filter.items()):
                    param_name = f"meta_val{i}"
                    where_clauses.append(f"chunk_metadata ->> '{key}' = :{param_name}")
                    params[param_name] = str(value)

            if datetime_from is not None:
                where_clauses.append("report_datetime_gmt >= :datetime_from")
                params["datetime_from"] = datetime_from

            if datetime_to is not None:
                where_clauses.append("report_datetime_gmt <= :datetime_to")
                params["datetime_to"] = datetime_to

            where_sql = f"WHERE { ' AND '.join(where_clauses)}" if where_clauses else ""

            query = text(
                f"""
                SELECT chunk_id, report_id, content, chunk_metadata, 
                    1 - (embedding <=> :query_vector) as similarity
                FROM report_chunks
                {where_sql}
                ORDER BY embedding <=> :query_vector
                LIMIT :top_k
            """
            )

            print(query.text % params)
            results = session.execute(query, params).mappings().all()

            return [
                RetrievedChunk(
                    chunk_id=row["chunk_id"],
                    content=row["content"],
                    report_id=row["report_id"],
                    metadata=row["chunk_metadata"],
                    similarity_score=row["similarity"],
                )
                for row in results
            ]
