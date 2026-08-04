import json
from app.repository.models import Report
from app.document_builder.document_builder import DocumentBuilder
from app.chunking.token_counter import TiktokenCounter
from app.chunking.section_chunker import SectionChunker
from datetime import datetime, timezone
from app.embeddings.factory import get_embedding_service, get_dry_run_limit, is_dry_run_enabled

SAMPLE_JSON_PATH = './scripts/sample_report.json'


def main() -> None:
    with open(SAMPLE_JSON_PATH) as f:
        raw_json = json.load(f)

    report = Report(
        report_id=raw_json['REPORTS']['REPORT_ID'],
        customer_name=raw_json['REPORTS']['CUSTOMER_NAME'],
        data_source=raw_json['REPORTS']['DATA_SOURCE'],
        imo=raw_json['REPORTS']['IMO'],
        report_type=raw_json['REPORTS']['REPORT_TYPE'],
        datetime_gmt=datetime.now(timezone.utc),
        raw_json=raw_json,
        zn_updated_at=datetime.now(timezone.utc),
    )

    document = DocumentBuilder().build(report=report)
    chunker = SectionChunker(token_counter=TiktokenCounter())
    chunks = chunker.chunk(document)

    print(f"Produced {len(chunks)} chunks for report_id={document.report_id}\n")
    for chunk in chunks:
        print(f'--- {chunk.chunk_id} ---')
        print(chunk.content)
        print(f"metadata: {chunk.metadata} \n")

    embedding_service = get_embedding_service()

    limit = get_dry_run_limit() if is_dry_run_enabled() else None

    embedded_chunks = embedding_service.embed_chunks(chunks=chunks, limit=limit)

    print('--- Embedded Chunks Start ---')
    print(embedded_chunks)
    print('--- Embedded Chunks End ---')
    print(f"Embedded {len(embedded_chunks)} of {len(chunks)} chunks "
      f"(dry_run={is_dry_run_enabled()})")
    


if __name__ == "__main__":
    main()
