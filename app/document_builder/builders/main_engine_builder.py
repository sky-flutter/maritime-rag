from app.document_builder.sections import SectionBuilder
from app.document_builder.models import DocumentSection


class MainEngineSectionBuilder(SectionBuilder):
    """MAIN_ENGINE is a list with a single snapshot record per report."""

    def build(self, raw_section: list[dict] | None) -> DocumentSection | None:
        if not raw_section:
            return None

        m = raw_section[0]
        content = (
            f"Main engine output {m.get('MAIN_ENGINE_OUTPUT')} kW at "
            f"{m.get('RPM')} RPM, running {m.get('MAIN_ENGINE_RUNNING_HOURS')} hours. "
            f"Power from torsiometer: {m.get('POWER_FROM_TORSIOMETER')} kW. "
            f"Turbocharger: {m.get('TURBO_CHARGER')} rpm."
        )
        return DocumentSection(name="main_engine", content=content, metadata={})