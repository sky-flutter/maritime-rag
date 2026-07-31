from app.document_builder.sections import SectionBuilder
from app.document_builder.models import DocumentSection


class ForobSectionBuilder(SectionBuilder):
    """FOROB (Fuel Oil Remaining On Board) is a list of one record per
    fuel type — no engine breakdown needed, unlike Consumption.
    """

    def build(self, raw_section: list[dict] | None) -> DocumentSection | None:
        if not raw_section:
            return None

        parts = [
            f"{r.get('FUEL_TYPE')}: {r.get('ROB')} mt"
            for r in raw_section
        ]
        content = "Fuel remaining on board — " + ", ".join(parts) + "."

        return DocumentSection(
            name="forob",
            content=content,
            metadata={"fuel_types": [r.get("FUEL_TYPE") for r in raw_section]},
        )