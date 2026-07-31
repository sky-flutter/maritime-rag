from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.chunking.chunker import Chunker
from app.chunking.token_counter import TokenCounter
from app.document_builder.models import Document, DocumentSection
from app.chunking.models import Chunk


class SectionChunker(Chunker):
    """Default strategy: one chunk per DocumentSection. If a section's
    content exceeds max_tokens, falls back to a RecursiveCharacterTextSplitter
    to split just that section into multiple chunks.
    """

    def __init__(
        self,
        token_counter: TokenCounter,
        max_tokens: int = 500,
        splitter_chunk_size: int = 1500,
        splitter_chunk_overlap: int = 150
    ) -> None:
        self._token_counter = token_counter
        self._max_tokens = max_tokens
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=splitter_chunk_size,
            chunk_overlap=splitter_chunk_overlap
        )

    def chunk(self, document: Document) -> list[Chunk]:
        chunks: list[Chunk] = []
        for section in document.sections:
            chunks.extend(self._chunk_section(document, section))

        return chunks

    def _chunk_section(
        self,
        document: Document,
        section: DocumentSection
    ) -> list[Chunk]:
        base_metadata = {**document.metadata, **
                         section.metadata, "section": section.name}
        if self._token_counter.count(section.content) <= self._max_tokens:
            return [
                Chunk(
                    chunk_id=f"{document.report_id}:{section.name}",
                    report_id=document.report_id,
                    content=section.content,
                    metadata=base_metadata
                )
            ]

        parts = self._splitter.split_text(section.content)
        return [
            Chunk(
                chunk_id=f"{document.report_id}:{section.name}:{i}",
                report_id=document.report_id,
                content=parts,
                metadata={**base_metadata, "part_index": i,
                          "part_count": len(parts)},
            )
            for i, part in enumerate(parts)
        ]
