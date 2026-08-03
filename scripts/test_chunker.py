import json
from app.repository.models import Report
from app.document_builder.document_builder import DocumentBuilder
from app.chunking.token_counter import TiktokenCounter
from app.chunking.section_chunker import SectionChunker
from datetime import datetime, timezone
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


if __name__ == "__main__":
    main()
