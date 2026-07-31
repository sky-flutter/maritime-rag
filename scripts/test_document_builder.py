import json

from app.document_builder.document_builder import DocumentBuilder
from app.repository.models import Report
from datetime import datetime, timezone

SAMPLE_JSON_PATH = "./scripts/sample_report.json"  # save your pasted JSON here


def main() -> None:
    with open(SAMPLE_JSON_PATH) as f:
        raw_json = json.load(f)

    report = Report(
        report_id=raw_json["REPORTS"]["REPORT_ID"],
        data_source=raw_json["REPORTS"]["DATA_SOURCE"],
        customer_name=raw_json["REPORTS"]["CUSTOMER_NAME"],
        imo=raw_json["REPORTS"]["IMO"],
        report_type=raw_json["REPORTS"]["REPORT_TYPE"],
        datetime_gmt=datetime.now(timezone.utc),
        raw_json=raw_json,
        zn_updated_at=datetime.now(timezone.utc)
    )

    builder = DocumentBuilder()
    document = builder.build(report)

    print(f"Document for report_id={document.report_id}")
    print(f"Document metadata: {document.metadata}\n")

    for section in document.sections:
        print(f"--- Section: {section.name} ---")
        print(section.content)
        print(f"Section metadata: {section.metadata}\n")


if __name__ == "__main__":
    main()