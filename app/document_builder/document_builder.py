from app.document_builder.builders.reports_builder import ReportsSectionBuilder
from app.document_builder.registry import build_default_registry
from app.document_builder.sections import SectionBuilder
from app.document_builder.models import Document
from app.repository.models import Report


class DocumentBuilder:
    """Orchestrates section builders to turn a Report into a Document.
    Knows nothing about the internals of any specific section — that
    knowledge lives entirely in the registered SectionBuilders.
    """

    def __init__(self, registry: dict[str, SectionBuilder] | None = None) -> None:
        self._registry = registry or build_default_registry()

    def build(self, report: Report) -> Document:
        sections = []
        for section_key, builder in self._registry.items():
            raw_section = report.raw_json.get(section_key)
            section = builder.build(raw_section)
            if section is not None:
                sections.append(section)

        metadata = self._extract_document_metadata(report)

        return Document(
            report_id=report.report_id,
            sections=sections,
            metadata=metadata,
        )

    def _extract_document_metadata(self, report: Report) -> dict:
        reports_builder = self._registry.get("REPORTS")
        if isinstance(reports_builder, ReportsSectionBuilder):
            return reports_builder.extract_document_metadata(
                report.raw_json.get("REPORTS")
            )
        return {}