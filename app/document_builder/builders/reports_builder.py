from app.document_builder.sections import SectionBuilder
from app.document_builder.models import DocumentSection


class ReportsSectionBuilder(SectionBuilder):
    """Builds the header section from the REPORTS block (a single dict,
    unlike the other sections which are lists).
    """

    def build(self, raw_section: dict | None) -> DocumentSection | None:
        if not raw_section:
            return None

        content = (
            f"Report type: {raw_section.get('REPORT_TYPE', 'unknown')} "
            f"(voyage #{raw_section.get('VOYAGE_NR', 'unknown')}). "
            f"Vessel condition: {raw_section.get('VESSEL_CONDITION', 'unknown')}. "
            f"Destination: {raw_section.get('DESTINATION_PORT', 'unknown')}. "
            f"Period: {raw_section.get('PERIOD_START_GMT')} to "
            f"{raw_section.get('PERIOD_END_GMT')} "
            f"({raw_section.get('PERIOD_DURATION_HOURS')} hours). "
            f"Logged distance: {raw_section.get('LOGGED_DISTANCE')} nm, "
            f"observed distance: {raw_section.get('OBSERVED_DISTANCE')} nm."
        )

        return DocumentSection(
            name="report_header",
            content=content,
            metadata={
                "imo": raw_section.get("IMO"),
                "voyage_nr": raw_section.get("VOYAGE_NR"),
                "report_type": raw_section.get("REPORT_TYPE"),
                "period_start_gmt": raw_section.get("PERIOD_START_GMT"),
                "period_end_gmt": raw_section.get("PERIOD_END_GMT"),
            },
        )

    def extract_document_metadata(self, raw_section: dict | None) -> dict:
        """Pulls fields useful for retrieval-time filtering, to attach
        at the Document level (not just this section).
        """
        if not raw_section:
            return {}
        return {
            "imo": raw_section.get("IMO"),
            "voyage_nr": raw_section.get("VOYAGE_NR"),
            "report_type": raw_section.get("REPORT_TYPE"),
            "vessel_condition": raw_section.get("VESSEL_CONDITION"),
        }