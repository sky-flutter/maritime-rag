from dataclasses import dataclass


@dataclass
class DocumentSection:
    name: str
    content: str
    metadata: str


@dataclass
class Document:
    report_id: str
    sections: list[DocumentSection]
    metadata: dict
