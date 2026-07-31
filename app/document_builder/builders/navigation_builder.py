from app.document_builder.sections import SectionBuilder
from app.document_builder.models import DocumentSection


class NavigationSectionBuilder(SectionBuilder):
    """NAVIGATION is a list with a single snapshot record per report."""

    def build(self, raw_section: list[dict] | None) -> DocumentSection | None:
        if not raw_section:
            return None

        n = raw_section[0]
        content = (
            f"Position: {n.get('LATITUDE')}, {n.get('LONGITUDE')}. "
            f"Course {n.get('COURSE')}°, speed over ground {n.get('SPEED_OVER_GROUND')} kn, "
            f"speed through water {n.get('SPEED_THROUGH_WATER')} kn. "
            f"Draft fore {n.get('DRAFT_FORE')} m, draft aft {n.get('DRAFT_AFTER')} m. "
            f"Time sailing {n.get('TIME_SAILING')} hours."
        )
        return DocumentSection(name="navigation", content=content, metadata={})